from rich.console import Console
from rich.table import Table
from typing import Annotated, Optional
from commands.query import print_queries
from database.query_repository import QueryRepository
from database.spreadsheet_repository import SpreadsheetRepository
from lib.sheet_writer import add_spreadsheet, populate_spreadsheet
from lib.util import option_prompt
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
        queries = query_repo.find_all()
        print_queries(queries)
        query = queries[option_prompt(queries, "Choose one of the categories by their number")]
    else:
        query = query_repo.find_by_id(q)

    if query is None:
        print(f"Query of if {q} not found")
        return

    spreadsheet = add_spreadsheet(query) 
    if spreadsheet and spreadsheet.id and typer.confirm("Do you want to populate the spreadsheet already?"):
        try:
            populate_spreadsheet(spreadsheet.id)
        except Exception as err:
            console.print("[bold red] Could not populate spreadsheet[/ bold red]")

@app.command()
def populate(s: Annotated[Optional[int], typer.Option(help="Id of the spreadsheet")] = None):
    if s:
        spreadsheet = spreadsheet_repo.find_by_id(s)
        if not spreadsheet:
            console.print(f"[bold red] Could not find or create spreadsheet[/ bold red]")
            return
    else:
        print_spreadsheets(spreadsheet_repo.find_all())
        s = spreadsheets_option_prompt()

    populate_spreadsheet(s)

@app.command()
def delete(s: Annotated[Optional[int], typer.Option(help="Id of the spreadsheet")] = None):
    if not s:
        s = spreadsheets_option_prompt()
    
    if typer.confirm("Are you sure you want to delete this spreadsheet?(It's not being deleted from google sheets)"):
        spreadsheet_repo.delete_by_id(s)

@app.command()
def listall():
    print_spreadsheets(spreadsheet_repo.find_all())

def spreadsheets_option_prompt() -> int:
    spreadsheets = spreadsheet_repo.find_all()
    print_spreadsheets(spreadsheets)
    id = typer.prompt("Choose a spreadsheet by their ID")
    while not spreadsheet_repo.exists_by_id(id):
        id = typer.prompt("Choose a valid ID")
    return id

