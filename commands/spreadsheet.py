from rich.console import Console
from rich.table import Table
from typing import Annotated, Optional
from commands.query import print_queries
from database.query_repository import QueryRepository
from database.spreadsheet_repository import SpreadsheetRepository
from error.Result import Result
from lib.sheet_writer import add_spreadsheet, populate_spreadsheet
from lib.util import option_prompt, print_error
from models import Spreadsheet
import typer

spreadsheet_repo = SpreadsheetRepository()
query_repo = QueryRepository()
app = typer.Typer()
console = Console()

def print_spreadsheets(spreadsheets: list[Spreadsheet]):
    if len(spreadsheets) == 0:
        console.print("[bold red]No spreadsheets available.[/bold red]")

    table = Table(title="Spreadsheets", expand=True)        
    table.add_column("ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("Term", justify="left", style="white")
    table.add_column("Query ID", justify="center", style="cyan")
    table.add_column("Google ID", justify="center", style="yellow")
    table.add_column("Is populated", justify="center", style="white")
    table.add_column("Link", justify="center", style="green")
    
    for spreadsheet in spreadsheets:
        table.add_row(
            str(spreadsheet.id),
            str(spreadsheet.query.term if spreadsheet.query else 'N/A'),
            str(spreadsheet.query.id if spreadsheet.query else 'N/A'),
            str(spreadsheet.google_id),
            str('Populated' if spreadsheet.is_populated else 'Not populated'),
            f"https://docs.google.com/spreadsheets/d/{spreadsheet.google_id}"
        ) 
    console.print(table)

@app.command()
def create(q: Annotated[Optional[int], typer.Option(help="Id of the query used to create a sheet")] = None):
    if q is None:
        queries_result = query_repo.find_all()
        if queries_result.value:
            queries = queries_result.value
            print_error(console, queries_result.error)
        else:
            print_error(console, queries_result.error)
            return

        print_queries(queries)
        query_result = query_repo.find_by_id(option_prompt(queries, "Choose one of the categories by their number"))
        if query_result.value:
            query = query_result.value
        else:
            print_error(console, queries_result.error)
            return
    else:
        query_result = query_repo.find_by_id(q)
        if query_result.value:
            query = query_result.value
            console.print(f"Query successfully created")
        else:
            print_error(console, query_result.error)
            return

    spreadsheet_result = add_spreadsheet(query) 
    if spreadsheet_result.value and spreadsheet_result.value.id and typer.confirm("Do you want to populate the spreadsheet already?"):
        populate_result = populate_spreadsheet(spreadsheet_result.value.id)
        if populate_result.error:
            print_error(console, populate_result.error)
    else: 
        print_error(console, spreadsheet_result.error)

@app.command()
def populate(s: Annotated[Optional[int], typer.Option(help="Id of the spreadsheet")] = None):
    if s:
        spreadsheet_result = spreadsheet_repo.find_by_id(s)
        if spreadsheet_result.value:
            populate_spreadsheet(s)
        else:
            print_error(console, spreadsheet_result.error)
            return
    else:
        spreadsheet_result = spreadsheet_repo.find_all()
        if spreadsheet_result.value:
            s_result = spreadsheets_option_prompt()
            if s_result.value:
                populate_spreadsheet(s_result.value)
        else:
            print_error(console, spreadsheet_result.error)


@app.command()
def delete(s: Annotated[Optional[int], typer.Option(help="Id of the spreadsheet")] = None):
    if not s: 
        s_result = spreadsheets_option_prompt()
        if s_result.value:
            s = s_result.value
        else:
            print_error(console, s_result.error)
            return
    
    if typer.confirm("Are you sure you want to delete this spreadsheet?(It's not being deleted from google sheets)"):
        delete_result = spreadsheet_repo.delete_by_id(s)
        if delete_result.error:
            print_error(console, delete_result.error)

@app.command()
def listall():
    spreadsheet_result = spreadsheet_repo.find_all()
    if spreadsheet_result.value and len(spreadsheet_result.value) > 0:
        print_spreadsheets(spreadsheet_result.value)
    else:
        print_error(console, spreadsheet_result.error)

def spreadsheets_option_prompt() -> Result[int, Exception]:
    spreadsheets_result = spreadsheet_repo.find_all()
    if spreadsheets_result.value: 
        print_spreadsheets(spreadsheets_result.value)
    else:
        print_error(console, spreadsheets_result.error)
        return Result(None, Exception("Could not find spreadsheets"))

    id = typer.prompt("Choose a spreadsheet by their ID")
    while not spreadsheet_repo.exists_by_id(id):
        id = typer.prompt("Choose a valid ID")
    return Result(id, None)

