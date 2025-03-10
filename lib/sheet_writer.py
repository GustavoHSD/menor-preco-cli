import datetime
from database.query_repository import QueryRepository
from database.spreadsheet_repository import SpreadsheetRepository
from googleapiclient.errors import HttpError
from context import google_credentials_context
from error.CouldNotPopulateSpreadsheet import CouldNotPopulateSpreadsheet
from error.Result import Result
from lib.scrapper import get_products
from lib.util import spinner
from models import Spreadsheet, Query, Sheet

@spinner(tasks=["Creating spreadsheet..."])
def add_spreadsheet(query: Query) -> Result[Spreadsheet, HttpError]:
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
        return Result(spreadsheet, None)
    except HttpError as error:
        return Result(None, error)

@spinner(tasks=["Fetching products...", "Populating sheets..."])
def populate_spreadsheet(id: int) -> Result[None, CouldNotPopulateSpreadsheet]:
    repo = SpreadsheetRepository()
    spreadsheet_result = repo.find_by_id(id)

    if not spreadsheet_result.value:
        return Result(None, CouldNotPopulateSpreadsheet(f"Could not find spreadsheet of id: {id} to populate"))

    if spreadsheet_result.error:
        return Result(None, CouldNotPopulateSpreadsheet(f"Could not find spreadsheet of id: {id} to populate", spreadsheet_result.error))

    spreadsheet = spreadsheet_result.value

    if not spreadsheet.query:
        return Result(None, CouldNotPopulateSpreadsheet(f"Spreadsheet of id: {id} missing query"))
        
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
        try:
            with google_credentials_context() as context:
                body = {
                    "requests": requests
                }
                (
                    context.service.spreadsheets()
                    .batchUpdate(spreadsheetId=spreadsheet.google_id, body=body)
                    .execute()
                )
        except HttpError as err:
            return Result(None, CouldNotPopulateSpreadsheet("Could not complete request to save sheets", err))
        sheets = __get_sheets(spreadsheet)
    
    requests = [] 
    for sheet in sheets: # build sheet request
        values = get_products(spreadsheet.query, spreadsheet.get_geohash(sheet.title))
        try:
            data = [[k for k in values[0].keys()]]
        except IndexError:
            continue
        product = []
        for value in values:
            data.append([v for v in value.values()])

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
     
    try:
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
    except HttpError as err:
        return Result(None, CouldNotPopulateSpreadsheet("Could not complete the request to populate spreadsheet", err))

    spreadsheet.is_populated = True
    spreadsheet.last_populated = datetime.datetime.now()

    save_spreadsheet_result = repo.save(spreadsheet)
    if save_spreadsheet_result.error:
        return Result(None, CouldNotPopulateSpreadsheet("Could not save spreadsheet to database", save_spreadsheet_result.error))
    return Result(None, None)

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
            try:
                sheets.append(Sheet(id, title, spreadsheet.get_geohash(title)))
            except Exception:
                continue
    return sheets
