"""
Configuracion para Wallapop Scraper Automation

"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '')

# Para testing local - RUTA CORREGIDA
LOCAL_CREDENTIALS_FILE = "../credentials/service-account.json"

# Para testing rapido, usar solo un vendedor
SELLERS_TEST = {
    "DURSAN D.": "https://es.wallapop.com/user/dursan-96099038"
}

# Vendedores divididos en grupos para ejecucion paralela
SELLERS_GROUP_1 = {
    # Vendedores más rápidos (menos anuncios)
    "DURSAN D.": "https://es.wallapop.com/user/dursan-96099038",
    "Beatriz D.": "https://es.wallapop.com/user/jhonnyg-324627202", 
    "GESTICAR G.": "https://es.wallapop.com/user/gesticarbilbao-76967810",
    "Garage Club C.": "https://es.wallapop.com/user/carlesb-25499485",
    "CARHAY.COM": "https://es.wallapop.com/user/carhaycom-67203195",
    "CRESTANEVADA S.L M.": "https://es.wallapop.com/user/grupoc-462243034"
}

SELLERS_GROUP_2 = {
    # Vendedores medianos
    "CRESTANEVADA VIC C.": "https://es.wallapop.com/user/grupoc-467547033",
    "CRESTANEVADA TOLEDO C.": "https://es.wallapop.com/user/crestanevadam-428487033",
    "CRESTANEVADA HUESCA C.": "https://es.wallapop.com/user/grupoc-459881034",
    "CRESTANEVADA MURCIA": "https://es.wallapop.com/user/antonio-425989040",
    "CRESTANEVADA ALMERIA C.": "https://es.wallapop.com/user/grupoc-460007033",
    "Mundicars G.": "https://es.wallapop.com/user/mundicarst-450893033"
}

SELLERS_GROUP_3 = {
    # Vendedores más grandes (más anuncios)
    "Mundicars V.": "https://es.wallapop.com/user/mundicarsv-460263033",
    "MundiCars B.": "https://es.wallapop.com/user/mundicarst-439083033",
    "MundiCars S.": "https://es.wallapop.com/user/mundicarst-443905034",
    "OCASIONPLUS E.": "https://es.wallapop.com/user/ocasionpluse-437961034",
    "GRUPO O.": "https://es.wallapop.com/user/grupoo-468103033",
    "Flexicar L.": "https://es.wallapop.com/user/flexicar-395335033",
    "INTEGRAL MOTION M.": "https://es.wallapop.com/user/integralm-463115034"
}

def get_sellers(test_mode=False, vendor_group=None):
    """Devuelve lista de vendedores segun el modo y grupo"""
    if test_mode:
        return SELLERS_TEST
    
    # Seleccionar grupo de vendedores para ejecucion paralela
    vendor_group = vendor_group or int(os.getenv('VENDOR_GROUP', '0'))
    
    if vendor_group == 1:
        return SELLERS_GROUP_1
    elif vendor_group == 2:
        return SELLERS_GROUP_2  
    elif vendor_group == 3:
        return SELLERS_GROUP_3
    else:
        # Si no se especifica grupo, devolver todos (modo original)
        all_sellers = {}
        all_sellers.update(SELLERS_GROUP_1)
        all_sellers.update(SELLERS_GROUP_2)
        all_sellers.update(SELLERS_GROUP_3)
        return all_sellers