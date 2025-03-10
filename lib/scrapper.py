from typing import Dict
import requests
from database.category_repository import CategoryRepository
from database.local_repository import LocalRepository
from error.EntityNotFound import EntityNotFound
from error.NoCategoriesFound import NoCategoriesFound
from error.NoLocalsDefined import NoLocalsDefined
from error.Result import Result
from lib.util import spinner
from models import Category, Local, Query
from constraints import URL, OFFSET

def get_products(query: Query, local: Local) -> list[Dict[str, str | float]]:
    '''
    Args: 
        query used to scrap data
    return: tuple containing the list of products found plus the amount of products
    '''
    if query.category is None:
        raise Exception("Category should not be None")
    
    request_url =f"{URL}/api/v1/produtos?local={local.geohash}&termo={query.term}&categoria={query.category.nota_id}&offset=0&raio={query.radius}&data=-1&ordem=0"
    res = requests.get(request_url)
    total = res.json()["total"]
    products = res.json()["produtos"]
    offset = 0
    while offset < total:
        products += requests.get(f"{URL}/api/v1/produtos?local={local.geohash}&termo={query.term}&categoria={query.category}&offset={offset}&raio={query.radius}&data=-1&ordem=0").json()["produtos"]
        offset += OFFSET

    products = [{   
        "Id": product["id"], 
        "Data de emissao": product["datahora"], 
        "Descricao": product["desc"], 
        "Distancia em km": product["distkm"], 
        "Id do estabelecimento": product["estabelecimento"]["codigo"],
        "Nome do estabelecimento": product["estabelecimento"]["nm_emp"],
        "Endereco": f"{product['estabelecimento']['tp_logr']} {product['estabelecimento']['nm_logr']}, N {product['estabelecimento']['nr_logr']}",
        "Codigo de barras": product["gtin"], 
        "Tempo": product["tempo"], 
        "Preco": float(product["valor"]), 
        "Valor de desconto": float(product["valor_desconto"])
    } for product in products]

    return products

def get_locals(region_names: list[str]) -> list[Local]:
    locals = []
    repo = LocalRepository()
    for name in region_names:
        local_result = repo.find_by_name(name)
        if isinstance(local_result.error, EntityNotFound) is True:
            res = requests.get(f"{URL}/mapa/search?regiao={name}")  
            data = res.json()
            try:
                local = Local(id=None, geohash=data[0]["geohash"], name=data[0]["display_name"].split(",")[0])
            except IndexError:
                print(f"City {name} not found")
                continue
            save_result = repo.save(local)
            if save_result.error:
                continue
        locals.append(local_result.value) 
    return locals
         
@spinner(["Buscando categorias..."])
def get_categories(query: Query) -> Result[list[Category], Exception]:
    repo = CategoryRepository()
    related_categories = []

    if len(query.locals) == 0:
        return Result(None, NoLocalsDefined(f"No locals defined for query of id: {query.id}"))

    for local in query.locals:
        res = requests.get(f"{URL}/api/v1/categorias?local={local}&termo={query.term}")
        data = res.json()
        for category in data["categorias"]:
            category = Category(id=None, nota_id=category["id"], description=category["desc"])
            category_result = repo.find_by_nota_id(id=category.nota_id)
            if not category_result.value:
                category_result = repo.save(category)
            if category_result.value not in related_categories:
                related_categories.append(category_result.value)

    if len(related_categories) == 0:
        return Result(None, NoCategoriesFound(f"No categories found for query of id: {query.id}")) 
    return Result(related_categories, None)

