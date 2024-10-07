import datetime
from database.query_repository import QueryRepository
from database.spreadsheet_repository import SpreadsheetRepository
from googleapiclient.errors import HttpError
from context import google_credentials_context
from lib.scrapper import get_products
from lib.util import spinner
from models import Spreadsheet, Query, Sheet

@spinner(tasks=["Creating spreadsheet..."])
def add_spreadsheet(query: Query) -> Spreadsheet | None:
    spreadsheet_repo = SpreadsheetRepository()
    query_repo = QueryRepository()
    spreadsheet = None
    now = datetime.datetime.now()
    try:
        with google_credentials_context() as context:
            body = {
                "properties": { "title": f"{query.term} - {now.strftime('%d/%m/%Y')}" }
            }
            response = (
                context.service.spreadsheets()
                .create(body=body, fields="spreadsheetId")
                .execute()
            )
            spreadsheet = Spreadsheet(id=None, google_id=response.get("spreadsheetId"), query=query)
            spreadsheet_repo.save(spreadsheet)
            query_repo.save(query)
        return spreadsheet
    except HttpError as error:
        print(f"An error occured: {error}")
        raise Exception("Could not finish request") 

@spinner(tasks=["Fetching products...", "Populating sheets..."])
def populate_spreadsheet(id: int):
    repo = SpreadsheetRepository()
    spreadsheet = repo.find_by_id(id)
    if not spreadsheet or not spreadsheet.query:
        print("Spreadsheet or query not found")
        return

    sheets = __get_sheets(spreadsheet)
    requests = []
    if len(sheets) == 0: # if no valid sheets are found create sheets
        for index, local in enumerate(spreadsheet.query.locals):
            requests.append({
                "addSheet": {
                    "properties": {
                        "title": local.name,
                        "index": index
                    }
                }
            })
        with google_credentials_context() as context:
            body = {
                "requests": requests
            }
            (
                context.service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet.google_id, body=body)
                .execute()
            )
        sheets = __get_sheets(spreadsheet)
    
    requests = [] 
    for sheet in sheets: # build sheet request
        values = get_products(spreadsheet.query, spreadsheet.get_geohash(sheet.title))
        try:
            data = [["id", "data de emissao", "descricao", "distancia em km", "id do estabelecimento", "nome do estabelecimento", "endereco do estabelecimento", "gtin", "ncm", "nrdoc", "tempo", "valor de venda", "valor de desconto"]]
        except IndexError:
            print(f"No products for term {spreadsheet.query.term} in local {sheet.title}")
            continue
        for value in values: 
            product = []
            for z in zip(value.__dict__.values()):
                product.append(z[0])
            data.append(product)

        rows = []
        for row in data:
            row_data = {
                "values": [{ "userEnteredValue": { "stringValue": str(cell) }} for cell in row]
            }
            rows.append(row_data)

        requests.append({
            "appendCells": {
                "sheetId": sheet.id,
                "rows": rows,
                "fields": "userEnteredValue"
            }
        })
     
    with google_credentials_context() as context:
        body = { 
            "requests": requests,
            "includeSpreadsheetInResponse": False,
            "responseIncludeGridData": False,
            "responseRanges": [],
        }
        
        (
            context.service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet.google_id, body=body)
            .execute()
        )
    spreadsheet.is_populated = True
    spreadsheet.last_populated = datetime.datetime.now()
    repo.save(spreadsheet)

def __get_sheets(spreadsheet: Spreadsheet) -> list[Sheet]:
    sheets = []
    with google_credentials_context() as context:
        response = (
            context.service.spreadsheets()
            .get(spreadsheetId=spreadsheet.google_id)
            .execute()
        )

        for sheet in response.get("sheets"):
            properties = sheet.get("properties")
            id = properties.get("sheetId")
            title = properties.get("title")
            #print(f"id: {id}, title: {title}")
            try:
                sheets.append(Sheet(id, title, spreadsheet.get_geohash(title)))
            except Exception:
                continue
    return sheets
