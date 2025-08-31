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

# Para testing rapido - CAMBIADO A GESTICAR PARA PROBAR PRECIOS MULTIPLES
SELLERS_TEST = {
    "GESTICAR G.": "https://es.wallapop.com/user/gesticarbilbao-76967810"
}

# OPCIONAL: Para testing con múltiples vendedores que tienen precios dobles
SELLERS_TEST_MULTIPLE = {
    "GESTICAR G.": "https://es.wallapop.com/user/gesticarbilbao-76967810",
    "Garage Club C.": "https://es.wallapop.com/user/carlesb-25499485"
}

# OPCIONAL: Para testing solo con DURSAN (precios únicos)
SELLERS_TEST_SIMPLE = {
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
    "Flexicar L.": "https://es.wallapop.com/user/flexicar-395335033",
    "INTEGRAL MOTION M.": "https://es.wallapop.com/user/integralm-463115034"
}

def get_sellers(test_mode=False, vendor_group=None, test_type="gesticar"):
    """División en 2 jobs basada en ejecución real de 6 horas"""
    if test_mode:
        if test_type == "dursan":
            return SELLERS_TEST_SIMPLE
        elif test_type == "multiple":
            return SELLERS_TEST_MULTIPLE
        else:
            return SELLERS_TEST
    
    vendor_group = vendor_group or os.getenv('VENDOR_GROUP', '0')
    
    if vendor_group == 'job1':
        # JOB 1: TODO LO QUE COMPLETÓ EN 6H (4,163 vehículos, ~4h 30m)
        # Grupos 1+2 + parte de grupo 3 que sí completó
        return {
            # SELLERS_GROUP_1 completo
            "DURSAN D.": "https://es.wallapop.com/user/dursan-96099038",
            "Beatriz D.": "https://es.wallapop.com/user/jhonnyg-324627202", 
            "GESTICAR G.": "https://es.wallapop.com/user/gesticarbilbao-76967810",
            "Garage Club C.": "https://es.wallapop.com/user/carlesb-25499485",
            "CARHAY.COM": "https://es.wallapop.com/user/carhaycom-67203195",
            "CRESTANEVADA S.L M.": "https://es.wallapop.com/user/grupoc-462243034",
            # SELLERS_GROUP_2 completo
            "CRESTANEVADA VIC C.": "https://es.wallapop.com/user/grupoc-467547033",
            "CRESTANEVADA TOLEDO C.": "https://es.wallapop.com/user/crestanevadam-428487033",
            "CRESTANEVADA HUESCA C.": "https://es.wallapop.com/user/grupoc-459881034",
            "CRESTANEVADA MURCIA": "https://es.wallapop.com/user/antonio-425989040",
            "CRESTANEVADA ALMERIA C.": "https://es.wallapop.com/user/grupoc-460007033",
            "Mundicars G.": "https://es.wallapop.com/user/mundicarst-450893033",
            # Parte de SELLERS_GROUP_3 que SÍ completó
            "Mundicars V.": "https://es.wallapop.com/user/mundicarsv-460263033",
            "MundiCars B.": "https://es.wallapop.com/user/mundicarst-439083033",
            "MundiCars S.": "https://es.wallapop.com/user/mundicarst-443905034",
            "OCASIONPLUS E.": "https://es.wallapop.com/user/ocasionpluse-437961034"
        }
        
    elif vendor_group == 'job2':
        # JOB 2: LO QUE NO COMPLETÓ + GRUPO O. (4,455 vehículos, ~5h 30m)
        return {
            "Flexicar L.": "https://es.wallapop.com/user/flexicar-395335033",
            "INTEGRAL MOTION M.": "https://es.wallapop.com/user/integralm-463115034"
        }
    
    # Mantener compatibilidad original para ejecución manual
    elif vendor_group == 1:
        return SELLERS_GROUP_1
    elif vendor_group == 2:
        return SELLERS_GROUP_2  
    elif vendor_group == 3:
        return SELLERS_GROUP_3
    else:
        # Todos los vendedores (solo para ejecución manual)
        all_sellers = {}
        all_sellers.update(SELLERS_GROUP_1)
        all_sellers.update(SELLERS_GROUP_2)
        all_sellers.update(SELLERS_GROUP_3)
        return all_sellers
