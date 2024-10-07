import os
from dotenv import load_dotenv

load_dotenv()

URL = "https://menorpreco.notaparana.pr.gov.br"
OFFSET = 50
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DATE_FORMAT = "%d-%m-%Y"

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
CLIENT_CREDENTIALS = os.getenv("CLIENT_CREDENTIALS")
TOKEN = os.getenv("TOKEN")
MODE = os.getenv("MODE")
