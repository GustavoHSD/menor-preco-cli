from rich.console import Console
from context import database_context
from database.category_repository import CategoryRepository
from database.local_repository import LocalRepository
from database.query_repository import QueryRepository
from database.spreadsheet_repository import SpreadsheetRepository
import typer
from commands import query, spreadsheet

local_repo = LocalRepository()
category_repo = CategoryRepository()
query_repo = QueryRepository()
spreadsheet_repo = SpreadsheetRepository()

app = typer.Typer()
app.add_typer(query.app, name="query")
app.add_typer(spreadsheet.app, name="spreadsheet")
console = Console()

def init_db():
    with open('schema.sql', 'r') as file:
        script = file.read()
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.executescript(script)

if __name__ == "__main__":
    init_db()
    app()

