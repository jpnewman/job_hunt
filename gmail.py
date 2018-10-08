#!/usr/bin/env python3

import re
import base64
import email
import bleach
import argparse
import hashlib

from io import BytesIO

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth2_file
from oauth2client import client, tools
from googleapiclient.errors import HttpError

from colorama import Fore, Back, Style, init

from datetime import datetime
from email.utils import parsedate_tz, mktime_tz
from email.header import decode_header

from bs4 import BeautifulSoup

from app.emails.models import Emails, EmailAttachments
from app import db


# Create DB
db.create_all()

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


class EmailFetchError(Exception):
    def __init__(self, message):
        self.message = message
        super(EmailFetchError, self).__init__(message)

    def __str__(self):
        return self.message


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True


def _get_service():
    store = oauth2_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return build('gmail', 'v1', http=creds.authorize(Http()))


def _get_messages(service,
                 user_id='me',
                 label_id=None,
                 query='is:unread',
                 max_results=100):
    try:
        if label_id is None:
            label_id = ['INBOX', 'IMPORTANT']

        response = service.users().messages().list(userId=user_id,
                                                   labelIds=label_id,
                                                   maxResults=max_results,
                                                   q=query).execute()

        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                                                       labelIds=label_id,
                                                       maxResults=max_results,
                                                       q=query,
                                                       pageToken=page_token).execute()

            if 'messages' in response:
                messages.extend(response['messages'])

        return messages

    except HttpError as error:
        print('An error occurred: {0}'.format(error))


def _get_raw_message_by_id(service, message_id, user_id='me'):
    response = service.users().messages().get(userId=user_id,
                                              id=message_id,
                                              format='raw').execute()

    if not response or 'raw' not in response:
        raise EmailFetchError('Error fetching email: User {0}, thread {1}'.
                              format(user_id, message_id))

    return base64.urlsafe_b64decode(response['raw']).decode('utf-8')


def _clean_html_email(html):
    soup = BeautifulSoup(html, 'html.parser')
    remove_tags = ['meta']
    
    for remove_tag in remove_tags:
        elements = soup.find_all(remove_tag)
        for element in elements:
            element.decompose()

    # Resolve Email CID image sources
    images = soup.find_all('img')
    for image in images:
        if image.has_attr('src'):
            if re.match('cid:.*', image['src']) is not None:
                del(image['src'])
                # image['src'] = ''

    return str(soup)


def _md5(bytes):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: bytes.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


# https://www.ianlewis.org/en/parsing-email-attachments-python
def _parse_attachment(message_part):
    content_disposition = message_part.get("Content-Disposition", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if content_disposition and dispositions[0].lower() == "attachment":
            file_data = message_part.get_payload(decode=True)
            attachment = BytesIO(file_data)
            attachment.content_type = message_part.get_content_type()
            attachment.size = len(file_data)
            attachment.name = None
            attachment.create_date = None
            attachment.mod_date = None
            attachment.read_date = None

            for param in dispositions[1:]:
                name, value = param.strip().split("=")
                name = name.lower()

                if name == "filename":
                    attachment.name = value
                elif name == "create-date":
                    attachment.create_date = value  # FIXME: datetime
                elif name == "modification-date":
                    attachment.mod_date = value # FIXME: datetime
                elif name == "read-date":
                    attachment.read_date = value # FIXME: datetime

            attachment.checksum = _md5(attachment)

            return attachment

    return None


def _parse_email(raw_message):
    body = ''
    html = ''
    attachments = []

    for part in raw_message.walk():
        attachment = _parse_attachment(part)
        if attachment:
            attachments.append(attachment)
        elif part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode(part.get_content_charset())
            body = bleach.clean(body, strip=True)
            body = body.replace('\n', '<br />')
            body = body.replace('\r', '<br />')
        elif part.get_content_type() == 'text/html':
            html = part.get_payload(decode=True).decode(part.get_content_charset())
            html = _clean_html_email(html)

    return {'body': body,
            'html': html,
            'attachments': attachments}


def _decode_msg_part(part):
    parts = []

    try:
        dc = decode_header(part)
    except HeaderParseError:
        return part

    for line, encoding in dc:
        if encoding is None:
            parts += str(line)
        else:
            parts += line.decode(encoding)

    return "".join(parts)


def add_messages_to_db(service,
                       query="is:starred is:unread",
                       max_download=None):
    print("Downloading Messages (Max: {0})...".format(max_download))

    messages = _get_messages(service=service,
                             query=query,
                             label_id=[])

    count = 0
    msg_obj = []
    for message in messages:
        raw = _get_raw_message_by_id(service, message['id'])

        msg_obj.append(raw)

        if max_download:
            count += 1
            if count >= max_download:
                break

    process_messages(messages=msg_obj)


def update_messages(max_download=None):
    service = _get_service()

    add_messages_to_db(service,
                       query="label:job-hunting",
                       max_download=max_download)


def reprocess_messages():
    messages = db.session.query(Emails).all()

    for message in messages:
        if message is not None:
            raw_message = ''.join([line for line in message.raw])
            process_email_message(raw_message=raw_message,
                                  email_obj=message,
                                  update_raw=False,
                                  update_attachments=False)
            db.session.commit()


def process_email_message(raw_message, email_obj, update_raw=True, update_attachments=True):
    msg = email.message_from_string(raw_message)

    date_tuple = parsedate_tz(msg['date'])
    if date_tuple:
        local_date = datetime.fromtimestamp(mktime_tz(date_tuple))
        email_obj.date = local_date

    email_obj.sender = _decode_msg_part(" ".join(msg['from'].split()[:-1]).strip('"'))
    
    address = msg['from'].split()[-1]
    email_obj.from_address = re.sub(r'[<>]','', address)
    
    message_id = msg['message-id'].strip()
    email_obj.message_id = re.sub(r'[<>]','', message_id)

    email_obj.subject = _decode_msg_part(msg['subject'])

    parsed_email = _parse_email(msg)

    email_obj.plain_text = parsed_email['body']
    email_obj.html = parsed_email['html']

    if update_attachments:
        for attachment in parsed_email['attachments']:
            attm = EmailAttachments()
            attm.name = attachment.name.strip('"')
            attm.size = attachment.size
            attm.content_type = attachment.content_type
            attm.create_date = attachment.create_date
            attm.mod_date = attachment.mod_date.strip('"')
            attm.read_date = attachment.read_date
            attm.checksum = attachment.checksum
            attm.binary = attachment.getvalue()

            email_obj.attachments.append(attm)

    if update_raw:
        email_obj.raw = raw_message


def process_messages(messages):
    print("Messages: {0}".format(len(messages)))
    for message in messages:
        email = Emails()
        process_email_message(raw_message=message,
                              email_obj=email)

        print("{0} - {1} ".format(email.message_id, email.date), end='')
        instance = db.session.query(Emails).filter_by(message_id=email.message_id,
                                                      date=email.date).first()

        if instance is None:
            db.session.add(email)
            db.session.commit()
            print(Fore.GREEN + "(Added)")
        else:
            print(Fore.BLUE + "(Exists)")


def _parse_args():
    desc = 'Update gmail Messages'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--reprocess',
                        action='store_true',
                        default=False,
                        help='Reprocess already downloaded messages')

    parser.add_argument('--max-download',
                        type=int,
                        default=None,
                        help='Max download')

    return parser.parse_args()


def main():
    # colorama init
    init(autoreset=True)

    args = _parse_args()

    if args.reprocess:
        reprocess_messages()
    else:
        update_messages(args.max_download)


if __name__ == '__main__':
    main()
