import typer
from typing import Annotated, List, Optional
from rich.console import Console
from rich.table import Table
from database.category_repository import CategoryRepository
from database.query_repository import QueryRepository
from lib.scrapper import get_categories, get_locals
from models import Query

query_repo = QueryRepository()
category_repo = CategoryRepository()
app = typer.Typer()
console = Console()

def print_categories(categories: list):
    table = Table(title="Categories") 
    table.add_column("Number", justify="center", style="cyan", no_wrap=True)
    table.add_column("ID", justify="center", style="magenta")
    table.add_column("Description", justify="left", style="green")
    
    for i, category in enumerate(categories):
        table.add_row(
            str(i),
            str(category.nota_id),
            str(category.description)
        )
    
    console.print(table)

def print_queries(queries: list[Query]):
    if len(queries) == 0:
        console.print("[bold red] No queries avaliable [/ bold red]")
        return
    table = Table(title="Queries", expand=True)        
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Term", justify="center", style="white")
    table.add_column("Category", justify="center", style="white")
    table.add_column("Regions", justify="center", style="yellow")

    for query in queries:
        table.add_row(
            str(query.id),
            str(query.term.replace("%20", ' ')),
            str(query.category.description if query.category else 'N/A'),
            str([f"{local.name}" for local in query.locals]),
        ) 
    console.print(table) 

@app.command()
def create(term: str, locals: Annotated[List[str], typer.Option()], radius: float):
    query = Query(id=None, term=term.replace(" ", "%20"), locals=get_locals(locals), category=None, radius=radius)
    categories = get_categories(query)
    print_categories(categories) 
    category_number = int(typer.prompt("Choose one of the categories by their number"))

    while len(categories) < category_number > len(categories):
        category_number = int(typer.prompt("Invalid number, try again"))
    query.category = categories[category_number]

    saved_query = query_repo.save(query)
    print_queries(queries=[saved_query])
        
@app.command()
def update(q: Annotated[int, typer.Option(help="Id of the query that you want to update")], 
           t: Annotated[Optional[str], typer.Option(help="Term of the query")] = None,
           c: Annotated[Optional[int], typer.Option(help="ID of the category")] = None):
    query = query_repo.find_by_id(q)
    if not query:
        console.print(f"[bold red] Query with id: {id} not found [/ bold red]")
        return
    if t:
        query.term = t.replace(" ", "%20")
    if c:
        query.category = category_repo.find_by_id(c)

    if t or c:
        query_repo.save(query)

@app.command()
def delete(q: Annotated[Optional[int], typer.Option(help="Id of the query that you want to update")]):
    if q:
        query = query_repo.find_by_id(q)
        if not query:
            console.print(f"[bold red] Query with id: {id} not found [/ bold red]")
            return
        if typer.confirm("Are you sure you want to permanently delete this query?"):
            query_repo.delete_by_id(q)
        return

@app.command()
def listall():
    print_queries(query_repo.find_all())

