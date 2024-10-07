from datetime import date as Date
from dataclasses import dataclass
from typing import Optional

from rich.table import Table

from error.RegionNotFound import RegionNotFound

@dataclass
class Store: 
    id: str 
    bairro: str 
    city: str 
    enterprise_name: str 
    number: str 
    tipo: str 
    uf: str 
    complement: str 
    street_name: str 

@dataclass
class Category:
    id: Optional[int]
    nota_id: str
    description: str
    def __eq__(self, value) -> bool:
        return self.id == value.id and \
            self.description.upper() == value.description.upper()

@dataclass
class Local:
    id: Optional[int]
    geohash: str
    name: str
    def __eq__(self, other) -> bool:
        return self.geohash == other.geohash and self.name.upper() == other.name.upper()

@dataclass
class Query:
    id: Optional[int]
    term: str
    locals: list[Local]
    category: Optional[Category]
    radius: float = 10

@dataclass
class Product:
    id: str  
    emission_date: Date  
    description: str  
    distkm: float  
    store_id: str  
    store_name: str  
    store_address: str
    gtin: str  
    ncm: str  
    nrdoc: str  
    tempo: str  
    value: float  
    discount_value: float  

@dataclass
class Sheet:
    id: str
    title: str
    local: Local

@dataclass
class Spreadsheet:
    google_id: str
    query: Optional[Query]
    id: Optional[int]
    is_populated: bool = False
    last_populated: Optional[Date] = None

    def get_geohash(self, region: str) -> Local:
        if not self.query:
            raise Exception(f"Query should be defined")
        for local in self.query.locals:
            if local.name == region:
                return local
        raise RegionNotFound(f"Could not find region {region}")
