import requests
from database.category_repository import CategoryRepository
from database.local_repository import LocalRepository
from lib.util import spinner
from models import Category, Local, Query, Product
from constraints import URL, OFFSET

def get_products(query: Query, local: Local) -> list[Product]:
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

    products = [Product(id=product["id"], 
                       emission_date=product["datahora"], 
                       description=product["desc"], 
                       distkm=product["distkm"], 
                       store_id=product["estabelecimento"]["codigo"],
                       store_name=product["estabelecimento"]["nm_emp"],
                       store_address=f"{product['estabelecimento']['tp_logr']} {product['estabelecimento']['nm_logr']}, N {product['estabelecimento']['nr_logr']}",
                       gtin=product["gtin"], 
                       ncm=product["ncm"], 
                       nrdoc=product["nrdoc"], 
                       tempo=product["tempo"], 
                       value=float(product["valor"]), 
                       discount_value=float(product["valor_desconto"]), 
                   ) for product in products]

    return products

def get_locals(region_names: list[str]) -> list[Local]:
    locals = []
    repo = LocalRepository()
    for name in region_names:
        local = repo.find_by_name(name)
        if local is None:
            res = requests.get(f"{URL}/mapa/search?regiao={name}")  
            data = res.json()
            local = Local(id=None, geohash=data[0]["geohash"], name=name)
            try:
                repo.save(local)
            except Exception:
                continue
        locals.append(local)
    return repo.find_all()

@spinner(["Buscando categorias..."])
def get_categories(query: Query) -> list[Category]:
    repo = CategoryRepository()
    related_categories = []
    if len(query.locals) == 0:
        raise Exception("Local should be defined")

    for local in query.locals:
        res = requests.get(f"{URL}/api/v1/categorias?local={local}&termo={query.term}")
        data = res.json()
        for category in data["categorias"]:
            category = Category(id=None, nota_id=category["id"], description=category["desc"])
            category_saved = repo.find_by_nota_id(id=category.nota_id)
            if not category_saved:
                category_saved = repo.save(category)
            if category_saved not in related_categories:
                related_categories.append(category_saved)
    return related_categories

