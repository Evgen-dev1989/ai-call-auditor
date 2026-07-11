import os
import time
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

SERVICE_ACCOUNT_FILE = 'service_credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


GOOGLE_MIME_TYPES = {
    'application/vnd.google-apps.spreadsheet': {
        'export_mime': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ext': '.xlsx'
    },
    'application/vnd.google-apps.document': {
        'export_mime': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'ext': '.docx'
    }
}



