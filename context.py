from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from contextlib import contextmanager
from constraints import CLIENT_CREDENTIALS, GOOGLE_APPLICATION_CREDENTIALS, MODE, SCOPES, TOKEN
from dataclasses import dataclass
import os
import sqlite3

@dataclass
class CredentialsContext:
    service: object

@contextmanager
def google_credentials_context():
    creds = None
    if GOOGLE_APPLICATION_CREDENTIALS is None:
        raise Exception("Credentials path should be especified")

    if TOKEN is None:
        raise Exception("Could not find token")

    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_CREDENTIALS, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN, "w") as token:
            token.write(creds.to_json())
    try:
        service = build("sheets", "v4", credentials=creds)
    except HttpError:
        raise Exception("Could not create sheets service")

    context = CredentialsContext(service)

    yield context

@contextmanager
def database_context():
    if MODE == "test":
        connection = sqlite3.connect("test_menor-preco.db")
    elif MODE == "dev":
        connection = sqlite3.connect("menor-preco.db")
    else:
        raise Exception(f"Mode should be test or dev, not {MODE}")
        
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()

