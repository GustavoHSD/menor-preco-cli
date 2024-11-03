import typer
from typing import Annotated, List, Optional
from rich.console import Console
from rich.table import Table
from database.category_repository import CategoryRepository
from database.query_repository import QueryRepository
from lib.scrapper import get_categories, get_locals
from lib.util import print_error
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
    locals_list = get_locals(locals)
    if len(locals_list) == 0:
        return
 
    query = Query(id=None, term=term.replace(" ", "%20"), locals=locals_list, category=None, radius=radius)
    categories_result = get_categories(query)
    if categories_result.value:
        categories = categories_result.value
    else:
        print_error(console, categories_result.error)
        return

    print_categories(categories) 
    category_number = int(typer.prompt("Choose one of the categories by their number"))

    while len(categories) < category_number > len(categories):
        category_number = int(typer.prompt("Invalid number, try again"))
    query.category = categories[category_number]

    query_result = query_repo.save(query)

    if query_result.value:
        print_queries(queries=[query_result.value])
    else:
        print_error(console, query_result.error)

@app.command()
def update(q: Annotated[int, typer.Option(help="Id of the query that you want to update")], 
           t: Annotated[Optional[str], typer.Option(help="Term of the query")] = None,
           c: Annotated[Optional[int], typer.Option(help="ID of the category")] = None):
    query_result = query_repo.find_by_id(q)
    if query_result.value:
        query = query_result.value
        if t:
            query.term = t.replace(" ", "%20")
        if c:
            category_result = category_repo.find_by_id(c)
            if category_result.value:
                query.category = category_result.value
            else:
                print_error(console, category_result.error)
                return
        if t or c:
            save_result = query_repo.save(query)
            if save_result.error:
                print_error(console, query_result.error)
                return
    else:
        print_error(console, query_result.error)

@app.command()
def delete(q: Annotated[Optional[int], typer.Option(help="Id of the query that you want to update")]):
    if q:
        query_result = query_repo.find_by_id(q)
        if query_result.value:
            if typer.confirm("Are you sure you want to permanently delete this query?"):
                delete_result = query_repo.delete_by_id(q)
                if delete_result.error:
                    print_error(console, delete_result.error)
        else: 
            print_error(console, query_result.error)

@app.command()
def listall():
    queries_result = query_repo.find_all()
    if queries_result.value:
        print_queries(queries_result.value)
    else:
        print_error(console, queries_result.error)

