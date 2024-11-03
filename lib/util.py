from datetime import datetime
import re
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import typer

from constraints import DATE_FORMAT

def alpha(n):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    return alphabet[(n - 1) % 26].upper()

def gen_range(values: list, sheet_name: str):
    columns_number = len([a for a in dir(values[0]) if not a.startswith('__')])
    return f"{sheet_name}!A1:{alpha(columns_number)}{len(values)+1}"

def spinner(tasks=[]):
    def wrapper(func):
        def wrapped_func(*args, **kwargs):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                for task in tasks:
                    task = progress.add_task(description=task, start=False)
                    progress.start_task(task)  # Start the task explicitly
                result = func(*args, **kwargs)
                progress.stop()  # Stop the progress after function completion
                return result
        return wrapped_func
    return wrapper
 
def option_prompt(options: list, message: str, invalid_message: str = "Inalid Number, try again") -> int:
    number = int(typer.prompt(message))
    if len(options) == 0:
        print(f"[bold red] No options available [/ bold red]")
        return -1
    while len(options) < number > len(options):
        number = int(typer.prompt(invalid_message))
    return number

def to_date(date: str | None):
    pattern = r"^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$"
    if date is None or re.match(pattern, date) is None:
        return None
    return datetime.strptime(date, DATE_FORMAT).date()

def print_error(console: Console, error: Exception | None):
    if error:
        console.print(f"[bold red] {error} [/ bold red]")
    console.print("[bold red] Something went wrong [/ bold red]")

    
