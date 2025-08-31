"""
================================================================================
                    WALLAPOP VEHICULOS - EXTRACTOR MOTICK                    
================================================================================

Descripcion: Sistema automatizado para extraccion de datos de vehiculos
             de vendedores profesionales en Wallapop con Google Sheets
             
Autor: Carlos Peraza
Version: 12.6
Fecha: Agosto 2025
Compatibilidad: Python 3.10+
Uso: Motick

================================================================================
"""

import time
import re
import os
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from colorama import Fore, init
from tqdm import tqdm
from config import get_sellers

init(autoreset=True)

def setup_browser():
    """Configuracion optimizada para GitHub Actions y local"""
    options = Options()
    
    # OPTIMIZACIONES CRITICAS PARA VELOCIDAD
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-images")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-domain-reliability")
    options.add_argument("--aggressive-cache-discard")
    options.add_argument("--memory-pressure-off")
    options.add_argument("--disable-background-media-suspend")
    options.add_argument("--disable-field-trial-config")
    options.add_argument("--disable-back-forward-cache")
    options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
    options.add_argument("--log-level=3")
    options.add_argument("--silent")
    
    # HEADLESS MODE para GitHub Actions
    if os.getenv('HEADLESS_MODE', 'false').lower() == 'true':
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
        print("MODO: Ejecutando en headless (GitHub Actions)")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-prompt-on-repost")
    options.add_argument("--disable-sync")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # CONFIGURACIONES AGRESIVAS DE RENDIMIENTO
    prefs = {
        "profile.default_content_setting_values": {
            "images": 2,
            "plugins": 2,
            "popups": 2,
            "geolocation": 2,
            "notifications": 2,
            "media_stream": 2,
        },
        "profile.managed_default_content_settings": {
            "images": 2
        }
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        browser = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Error iniciando Chrome: {e}")
        # Fallback para diferentes entornos
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=options)
    
    # TIMEOUTS MAS AGRESIVOS PERO SEGUROS
    browser.implicitly_wait(0.3)
    browser.set_page_load_timeout(6)
    browser.set_script_timeout(3)
    
    browser.maximize_window()
    return browser

def setup_google_sheets():
    """Configurar Google Sheets uploader desde variables de entorno"""
    try:
        from google_sheets_uploader import GoogleSheetsUploader
        
        # Variables de entorno (GitHub Actions)
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        if credentials_json and sheet_id:
            # Modo GitHub Actions
            return GoogleSheetsUploader(
                credentials_json_string=credentials_json,
                sheet_id=sheet_id
            )
        else:
            # Modo local - usar archivo de credenciales
            from config import LOCAL_CREDENTIALS_FILE
            if os.path.exists(LOCAL_CREDENTIALS_FILE) and sheet_id:
                return GoogleSheetsUploader(
                    credentials_file=LOCAL_CREDENTIALS_FILE,
                    sheet_id=sheet_id
                )
            else:
                print("AVISO: Google Sheets no configurado")
                return None
                
    except ImportError:
        print("AVISO: Google Sheets uploader no disponible")
        return None
    except Exception as e:
        print(f"ERROR configurando Google Sheets: {e}")
        return None

def print_extraction_summary(seller_name, title, precio_contado, precio_financiado, attributes, url, main_data):
    """Muestra resumen de la extraccion con informacion de errores"""
    print(f"\n{'-' * 60}")
    print(f"VEHICULO EXTRAIDO")
    print(f"{'-' * 60}")
    print(f"Vendedor: {seller_name}")
    print(f"Titulo: {title}")
    
    # MOSTRAR ERRORES PARA IDENTIFICAR PROBLEMAS
    if not title or title == "No disponible":
        print(f"  [ERROR] Titulo vacio o no encontrado")
    if "No especificado" in precio_contado:
        print(f"  [ERROR] Precio contado no encontrado")
    if main_data.get("km") == "No especificado":
        print(f"  [ERROR] KM no encontrados")
    
    print(f"Precio Contado: {precio_contado}")
    print(f"Precio Financiado: {precio_financiado}")
    
    # Mostrar datos principales
    print(f"Año: {main_data.get('año', 'No especificado')}")
    print(f"KM: {main_data.get('km', 'No especificado')}")
    
    if attributes:
        print("Caracteristicas:")
        for key, value in attributes.items():
            print(f"  {key.title()}: {value}")
    
    print(f"URL: {url[:60]}...")
    print(f"Extraccion completada")
    print(f"{'-' * 60}\n")

def detect_monthly_price(price_text, seller_name):
    """Detecta si un precio es mensual basado en el valor y vendedor"""
    if not price_text or price_text.strip() == "":
        return "No especificado"
        
    try:
        # Limpiar el texto primero
        clean_text = price_text.replace('&nbsp;', ' ').replace('\xa0', ' ').strip()
        if not clean_text:
            return "No especificado"
        
        # Extraer número del precio
        price_match = re.search(r'(\d+(?:\.\d{3})*)', clean_text.replace(',', ''))
        if not price_match:
            return clean_text  # Si no encuentra match, devuelve el texto limpio
        
        price_value = int(price_match.group(1).replace('.', ''))
        
        # CRESTANEVADA suele mostrar precios mensuales como precios totales
        crestanevada_keywords = ['CRESTANEVADA', 'crestanevada']
        is_crestanevada = any(keyword in seller_name for keyword in crestanevada_keywords)
        
        # Si es CRESTANEVADA y el precio es menor a 1000€, probablemente es mensual
        if is_crestanevada and price_value < 1000:
            return f"{price_value} €/mes"
        
        # Para otros vendedores, precios muy bajos también pueden ser mensuales
        elif price_value < 500:
            return f"{price_value} €/mes"
        
        return clean_text
        
    except Exception as e:
        return price_text if price_text else "No especificado"

def extract_car_data(driver, url, seller_name):
    """Extrae datos del coche - VERSION FINAL SIN DEBUG"""
    try:
        driver.get(url)
        time.sleep(1.5)
        
        # TITULO - MULTIPLES ESTRATEGIAS CON ESPERA OPTIMIZADA
        title = ""
        title_selectors = [
            "h1.item-detail_ItemDetailTwoColumns__title__VtWrR",
            "h1",
            ".item-detail_ItemDetailTwoColumns__title__VtWrR",
            "[class*='title']"
        ]
        
        for selector in title_selectors:
            try:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.text.strip():
                    title = element.text.strip()
                    break
            except:
                continue
        
        # Si no encuentra titulo, usar URL como backup
        if not title:
            title = url.split('/')[-1].replace('-', ' ').title()
        
        # LIMPIAR NUMERO ID DEL FINAL DEL TITULO
        title = re.sub(r'\s*\d{10,}$', '', title)
        
        # PRECIOS - EXTRACCION CORREGIDA
        precio_contado = "No especificado"
        precio_financiado = "No especificado"
        
        # ESPERAR A QUE CARGUEN LOS PRECIOS
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '€')]"))
            )
        except:
            pass
        
        # 1. BUSCAR PRECIO AL CONTADO POR ETIQUETA
        try:
            contado_elements = driver.find_elements(By.XPATH, 
                "//span[text()='Precio al contado']/following::span[contains(@class, 'ItemDetailPrice') and contains(text(), '€')]"
            )
            
            if contado_elements:
                raw_price = contado_elements[0].text.strip()
                precio_contado = detect_monthly_price(raw_price, seller_name)
        except:
            pass
        
        # 2. BUSCAR PRECIO FINANCIADO POR ETIQUETA
        try:
            financiado_elements = driver.find_elements(By.XPATH, 
                "//span[text()='Precio financiado']/following::span[contains(@class, 'ItemDetailPrice') and contains(text(), '€')]"
            )
            
            if financiado_elements:
                raw_price = financiado_elements[0].text.strip()
                precio_financiado = detect_monthly_price(raw_price, seller_name)
        except:
            pass
        
        # 3. FALLBACK: USAR SELECTORES CSS ESPECÍFICOS
        if precio_contado == "No especificado":
            price_selectors_contado = [
                "span.item-detail-price_ItemDetailPrice--standardFinanced__f9ceG",
                ".item-detail-price_ItemDetailPrice--standardFinanced__f9ceG", 
                "span.item-detail-price_ItemDetailPrice--standard__fMa16",
                "[class*='standardFinanced'] span"
            ]
            
            for selector in price_selectors_contado:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and '€' in text:
                            precio_contado = detect_monthly_price(text, seller_name)
                            break
                    if precio_contado != "No especificado":
                        break
                except:
                    continue
        
        if precio_financiado == "No especificado":
            price_selectors_financiado = [
                "span.item-detail-price_ItemDetailPrice--financed__LgMRH",
                ".item-detail-price_ItemDetailPrice--financed__LgMRH",
                "[class*='financed'] span"
            ]
            
            for selector in price_selectors_financiado:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and '€' in text:
                            precio_financiado = detect_monthly_price(text, seller_name)
                            break
                    if precio_financiado != "No especificado":
                        break
                except:
                    continue
        
        # 4. ÚLTIMO FALLBACK: BUSCAR CUALQUIER PRECIO
        if precio_contado == "No especificado":
            try:
                price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
                
                valid_prices = []
                for i, elem in enumerate(price_elements[:10]):
                    try:
                        text = elem.text.strip().replace('&nbsp;', ' ').replace('\xa0', ' ')
                        if not text:
                            continue
                        
                        # REGEX PARA CAPTURAR PRECIOS REALISTAS
                        price_patterns = [
                            r'(\d{1,3}(?:\.\d{3})+)\s*€',
                            r'(\d{1,6})\s*€'
                        ]
                        
                        for pattern in price_patterns:
                            price_matches = re.findall(pattern, text)
                            for price_match in price_matches:
                                try:
                                    price_clean = price_match.replace('.', '')
                                    price_value = int(price_clean)
                                    
                                    if 50 <= price_value <= 300000:
                                        formatted_price = f"{price_value:,}".replace(',', '.') + " €" if price_value >= 1000 else f"{price_value} €"
                                        final_price = detect_monthly_price(formatted_price, seller_name)
                                        valid_prices.append((price_value, final_price, text))
                                except:
                                    continue
                    except:
                        continue
                
                # Tomar el precio más alto como precio al contado
                if valid_prices:
                    valid_prices = sorted(set(valid_prices), key=lambda x: x[0], reverse=True)
                    precio_contado = valid_prices[0][1]
                        
            except:
                pass
        
        # CARACTERISTICAS - SELECTOR VERIFICADO
        attributes = extract_car_attributes(driver)
        
        # DATOS ADICIONALES DEL HTML
        main_data = extract_main_car_info_from_html(driver)
        
        # EXTRAER MARCA Y MODELO COMPLETO DEL TITULO
        marca, modelo_completo = extract_brand_and_full_model_from_title(title)
        
        # Logging visual limpio
        print_extraction_summary(seller_name, title, precio_contado, precio_financiado, attributes, url, main_data)
        
        return {
            "Marca": main_data.get("marca", marca),
            "Modelo": modelo_completo,
            "Vendedor": seller_name,
            "Año": main_data.get("año", "No especificado"),
            "KM": main_data.get("km", "No especificado"),
            "Precio al Contado": precio_contado,
            "Precio Financiado": precio_financiado,
            "Tipo": attributes.get("tipo", "No especificado"),
            "Nº Plazas": attributes.get("plazas", "No especificado"),
            "Nº Puertas": attributes.get("puertas", "No especificado"),
            "Combustible": attributes.get("combustible", "No especificado"),
            "Potencia": format_power(attributes.get("potencia", "No especificado")),
            "Conducción": attributes.get("conduccion", "No especificado"),
            "URL": url,
            "Fecha Extracción": datetime.now().strftime("%d/%m/%Y")
        }
    except Exception as e:
        print(f"ERROR en {url}: {str(e)}")
        return None

def extract_car_attributes(driver):
    """Extrae atributos usando selector verificado"""
    attributes = {}
    
    try:
        attribute_elements = driver.find_elements(By.CSS_SELECTOR, "span.item-detail-attributes-info_AttributesInfo__measure__O9xR3")
        
        for element in attribute_elements:
            text = element.text.strip()
            text_lower = text.lower()
            
            # CLASIFICAR ATRIBUTOS
            if "plazas" in text_lower:
                attributes["plazas"] = text
            elif "puertas" in text_lower:
                attributes["puertas"] = text
            elif any(word in text_lower for word in ["gasolina", "diésel", "diesel", "eléctrico", "electrico", "híbrido", "hibrido", "gas", "gnc", "glp", "etanol"]):
                attributes["combustible"] = text
            elif "caballos" in text_lower or "cv" in text_lower:
                attributes["potencia"] = text
            elif any(word in text_lower for word in ["manual", "automático", "automatico", "automática", "automatica"]):
                attributes["conduccion"] = text
            elif any(word in text_lower for word in ["pequeño", "grande", "mediano", "familiar", "monovolumen", "todoterreno", "furgoneta", "4x4", "suv", "berlina", "deportivo", "coupé", "coupe", "cabrio", "descapotable", "sedán", "sédan", "compacto", "utilitario"]):
                attributes["tipo"] = text
                
        return attributes
        
    except:
        return {}

def extract_main_car_info_from_html(driver):
    """Extrae datos adicionales del HTML completo de la pagina - CORREGIDO CON ACENTOS"""
    main_data = {}
    
    try:
        # EXTRAER KILOMETROS CON SELECTOR ESPECIFICO - CORREGIDO CON ACENTO
        try:
            km_section = driver.find_element(By.XPATH, "//span[text()='Kilómetros']/following-sibling::span")
            km_text = km_section.text.strip()
            if km_text and km_text.replace('.', '').replace(',', '').replace(' ', '').isdigit():
                km_clean = km_text.replace('.', '').replace(',', '').replace(' ', '')
                km_value = int(km_clean)
                main_data["km"] = format_kilometers(str(km_value))
        except:
            # Fallback optimizado: buscar en HTML de forma mas eficiente
            try:
                html_content = driver.page_source
                km_patterns = [
                    r'Kilómetros["\s:>]*</span><span[^>]*>(\d+(?:[\.\s]\d+)*)</span>',
                    r'kilómetros["\s:>]*</span><span[^>]*>(\d+(?:[\.\s]\d+)*)</span>',
                    r'>(\d{4,7})\s*km',
                    r'(\d{4,7})\s*kilómetros'
                ]
                
                for pattern in km_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        try:
                            km_clean = match.replace('.', '').replace(',', '').replace(' ', '')
                            km_value = int(km_clean)
                            if 100 <= km_value <= 999999:  # Rango ampliado
                                main_data["km"] = format_kilometers(str(km_value))
                                break
                        except:
                            continue
                    if "km" in main_data:
                        break
            except:
                pass
        
        # EXTRAER AÑO - CORREGIDO CON ACENTO
        try:
            year_section = driver.find_element(By.XPATH, "//span[text()='Año']/following-sibling::span")
            year_text = year_section.text.strip()
            if year_text.isdigit() and 1990 <= int(year_text) <= 2025:
                main_data["año"] = year_text
        except:
            # Fallback mas rapido
            try:
                html_content = driver.page_source
                year_patterns = [
                    r'Año["\s:>]*</span><span[^>]*>(\d{4})</span>',
                    r'año["\s:>]*</span><span[^>]*>(\d{4})</span>'
                ]
                
                for pattern in year_patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        year = int(match)
                        if 1990 <= year <= 2025:
                            main_data["año"] = str(year)
                            break
                    if "año" in main_data:
                        break
            except:
                pass
        
        # EXTRAER MARCA DEL HTML - OPTIMIZADO
        try:
            marca_section = driver.find_element(By.XPATH, "//span[text()='Marca']/following-sibling::*")
            marca_text = marca_section.text.strip()
            if marca_text and len(marca_text) > 1:
                main_data["marca"] = marca_text.title()
        except:
            pass
        
        return main_data
        
    except:
        return {}

def extract_brand_and_full_model_from_title(title):
    """Extrae marca y modelo COMPLETO del titulo - OPTIMIZADO"""
    if not title or title == "No disponible":
        return "No especificado", "No especificado"
    
    # LIMPIAR TITULO: eliminar numeros ID del final
    title_clean = re.sub(r'\s*\d{10,}$', '', title)
    
    title_lower = title_clean.lower()
    brands = {
        # MARCAS PRINCIPALES EXISTENTES (lista original)
        "audi": "Audi", "bmw": "BMW", "mercedes": "Mercedes-Benz", "volkswagen": "Volkswagen",
        "vw": "Volkswagen", "seat": "Seat", "ford": "Ford", "opel": "Opel", "peugeot": "Peugeot",
        "renault": "Renault", "citroën": "Citroën", "citroen": "Citroën", "toyota": "Toyota",
        "nissan": "Nissan", "honda": "Honda", "mazda": "Mazda", "hyundai": "Hyundai",
        "kia": "Kia", "fiat": "Fiat", "alfa": "Alfa Romeo", "volvo": "Volvo", "skoda": "Skoda",
        "dacia": "Dacia", "suzuki": "Suzuki", "mitsubishi": "Mitsubishi", "subaru": "Subaru",
        "lexus": "Lexus", "infiniti": "Infiniti", "jeep": "Jeep", "land": "Land Rover",
        "jaguar": "Jaguar", "porsche": "Porsche", "mini": "Mini", "smart": "Smart",
        "tesla": "Tesla", "chevrolet": "Chevrolet", "cupra": "Cupra", "ssangyong": "Ssangyong",
        "iveco": "Iveco", "ds": "DS",
        
        # MARCAS IMPORTANTES - ACTUALES EN ESPAÑA
        "lancia": "Lancia",                    # Italiana, se vende en España
        "mg": "MG",                            # China, creciente en España
        "alpine": "Alpine",                    # Francesa, deportivos
        "polestar": "Polestar",                # Volvo eléctrica, creciente
        "byd": "BYD",                          # China, entrando fuerte en Europa
        "genesis": "Genesis",                  # Hyundai premium
        "acura": "Acura",                      # Honda premium (menos común)
        "cadillac": "Cadillac",                # Americana
        "chrysler": "Chrysler",                # Americana  
        "dodge": "Dodge",                      # Americana
        "ram": "Ram",                          # Dodge comerciales (separada desde 2010)
        "isuzu": "Isuzu",                      # Japonesa, principalmente comerciales
        "lynk": "Lynk & Co",                   # China, entrando en Europa
        "maxus": "Maxus",                      # China, furgonetas principalmente
        
        # MARCAS PREMIUM/SUPERCAR (presentes en mercado español)
        "maserati": "Maserati",
        "ferrari": "Ferrari", 
        "lamborghini": "Lamborghini",
        "bentley": "Bentley",
        "rolls": "Rolls-Royce", "rollsroyce": "Rolls-Royce",
        "aston": "Aston Martin", "astonmartin": "Aston Martin",
        "mclaren": "McLaren",
        "lotus": "Lotus",
        "bugatti": "Bugatti",
        "koenigsegg": "Koenigsegg",
        "pagani": "Pagani",
        "morgan": "Morgan",
        
        # MARCAS HISTÓRICAS/DESAPARECIDAS (coches usados en Wallapop)
        "saab": "Saab",                       # Sueca, desaparecida pero muchos usados
        "rover": "Rover",                     # Británica, desaparecida
        "pontiac": "Pontiac",                 # Americana, desaparecida
        "oldsmobile": "Oldsmobile",           # Americana, desaparecida
        "plymouth": "Plymouth",               # Americana, desaparecida
        "mercury": "Mercury",                 # Ford, desaparecida
        "saturn": "Saturn",                   # GM, desaparecida
        "hummer": "Hummer",                   # GM, desaparecida (pero revivida eléctrica)
        "scion": "Scion",                     # Toyota, desaparecida
        "daewoo": "Daewoo",                   # Coreana, ahora parte de GM/Chevrolet
        "austin": "Austin",                   # Británica, histórica
        "morris": "Morris",                   # Británica, histórica
        "triumph": "Triumph",                 # Británica, histórica
        "santana": "Santana",                 # Española, desaparecida
        "pegaso": "Pegaso",                   # Española, histórica
        
        # MARCAS COMERCIALES/INDUSTRIALES
        "man": "MAN",
        "scania": "Scania", 
        "daf": "DAF",
        "renault trucks": "Renault Trucks", "renaulttrucks": "Renault Trucks",
        "volvo trucks": "Volvo Trucks", "volvotrucks": "Volvo Trucks",
        "hino": "Hino",                       # Toyota comerciales
        "freightliner": "Freightliner",
        "kenworth": "Kenworth",
        "peterbilt": "Peterbilt",
        "mack": "Mack",
        
        # VARIANTES Y ALIAS IMPORTANTES
        "mercedes-benz": "Mercedes-Benz", "mercedesbenz": "Mercedes-Benz",
        "range": "Land Rover", "rangerover": "Land Rover", "range rover": "Land Rover",
        "land rover": "Land Rover", "landrover": "Land Rover",
        "alfa romeo": "Alfa Romeo", "alfaromeo": "Alfa Romeo",
        "rolls royce": "Rolls-Royce",
        "aston martin": "Aston Martin",
        "lynk & co": "Lynk & Co", "lynkco": "Lynk & Co",
        "great wall": "Great Wall", "greatwall": "Great Wall",
        
        # SUBMARCAS/DIVISIONES DEPORTIVAS (pueden aparecer en títulos)
        "amg": "Mercedes-AMG",                # Mercedes deportivo
        "m": "BMW M",                         # BMW deportivo  
        "rs": "Audi RS",                      # Audi deportivo
        "maybach": "Mercedes-Maybach",        # Mercedes ultra-premium
        "brabus": "Brabus",                   # Tuner Mercedes
        "alpina": "Alpina",                   # Tuner BMW
        "abarth": "Abarth",                   # Fiat deportivo
        "nismo": "Nissan Nismo",              # Nissan deportivo
        "sti": "Subaru STI",                  # Subaru deportivo
        "type": "Honda Type R",               # Honda deportivo
        "si": "Honda Si",                     # Honda deportivo
        "vxr": "Opel VXR",                    # Opel deportivo
        "opc": "Opel OPC",                    # Opel deportivo
        "gti": "Volkswagen GTI",              # VW deportivo
        "gtr": "Nissan GT-R",                 # Nissan deportivo
        
        # ELÉCTRICAS EMERGENTES
        "fisker": "Fisker",
        "rivian": "Rivian", 
        "lucid": "Lucid",
        "nio": "NIO",
        "xpeng": "XPeng",
        "li auto": "Li Auto", "liauto": "Li Auto",
        "zeekr": "Zeekr",
        "aiways": "Aiways",
        "ora": "ORA",                        # Great Wall eléctrica
        "wey": "WEY",                        # Great Wall premium
        "haval": "Haval",                    # Great Wall SUV
        
        # OTRAS MARCAS CHINAS CON PRESENCIA CRECIENTE
        "chery": "Chery",
        "geely": "Geely", 
        "dongfeng": "Dongfeng",
        "jac": "JAC",
        "baic": "BAIC",
        "foton": "Foton",
        "ldv": "LDV",
        
        # CASOS ESPECIALES Y ERRORES COMUNES
        "mercedes": "Mercedes-Benz",          # Alias común
        "benz": "Mercedes-Benz",              # Alias común
        "beemer": "BMW", "bimmer": "BMW",     # Alias populares BMW
        "lambo": "Lamborghini",               # Alias popular
        "ferrari": "Ferrari", "fiat": "Fiat", # Separar bien Fiat/Ferrari
        "rr": "Rolls-Royce",                  # Alias común RR
        "rrs": "Land Rover",                  # Range Rover Sport
        "disco": "Land Rover",                # Discovery alias
    }
    
    # ESTRATEGIA OPTIMIZADA: Buscar marca en la primera palabra primero
    words = title_clean.split()
    if words:
        first_word_lower = words[0].lower()
        
        # Buscar coincidencia exacta con primera palabra
        for brand_key, brand_name in brands.items():
            if brand_key == first_word_lower:
                modelo_completo = " ".join(words[1:]) if len(words) > 1 else "No especificado"
                return brand_name, modelo_completo
        
        # Si no encuentra coincidencia exacta, buscar si la primera palabra contiene la marca
        for brand_key, brand_name in brands.items():
            if brand_key in first_word_lower:
                modelo_completo = " ".join(words[1:]) if len(words) > 1 else "No especificado"
                return brand_name, modelo_completo
    
    # FALLBACK: Buscar marca en cualquier parte del titulo
    marca_encontrada = "No especificado"
    posicion_marca = -1
    
    for brand_key, brand_name in brands.items():
        if brand_key in title_lower:
            marca_encontrada = brand_name
            posicion_marca = title_lower.find(brand_key)
            break
    
    # Extraer el modelo completo (todo despues de la marca)
    if posicion_marca != -1:
        words = title_clean.split()
        modelo_parts = []
        marca_encontrada_en_titulo = False
        
        for word in words:
            if not marca_encontrada_en_titulo:
                if any(brand_key in word.lower() for brand_key in brands.keys()):
                    marca_encontrada_en_titulo = True
                    continue
            else:
                modelo_parts.append(word)
        
        modelo_completo = " ".join(modelo_parts) if modelo_parts else "No especificado"
        return marca_encontrada, modelo_completo
    
    # ULTIMO RECURSO: Primera palabra como marca, resto como modelo
    if words:
        return words[0].title(), " ".join(words[1:]) if len(words) > 1 else "No especificado"
    
    return "No especificado", "No especificado"

def format_kilometers(km_text):
    """Formatea kilometraje"""
    if km_text == "No especificado" or not km_text:
        return "No especificado"
    try:
        numbers = re.findall(r'\d+', str(km_text))
        if numbers:
            km_value = int(''.join(numbers))
            return f"{km_value:,} km".replace(',', '.')
    except:
        pass
    return str(km_text)

def format_power(power_text):
    """Formatea potencia"""
    if power_text == "No especificado" or not power_text:
        return "No especificado"
    try:
        numbers = re.findall(r'\d+', str(power_text))
        if numbers:
            return f"{numbers[0]} CV"
    except:
        pass
    return str(power_text)

def find_and_click_load_more_button(driver):
    """Busca y hace clic en el botón 'Ver más productos' - SELECTORES CORREGIDOS PARA WEB COMPONENTS"""
    try:
        # Scroll más eficiente con tiempo suficiente
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.0)  # Tiempo aumentado
        
        # NUEVOS SELECTORES BASADOS EN HTML REAL DE WALLAPOP
        button_selectors = [
            # Web component selector - el más probable
            'walla-button[text="Ver más productos"]',
            # Button interno del web component
            'button.walla-button__button--primary',
            # Por clase CSS específica
            '.walla-button__button--primary',
            # XPath por span interno con texto
            '//span[text()="Ver más productos"]/ancestor::button',
            # XPath por walla-button con atributo text
            '//walla-button[@text="Ver más productos"]',
            # XPath por contenido de texto en cualquier parte
            '//*[contains(text(), "Ver más productos")]',
            # Fallback genérico por clase
            '//button[contains(@class, "walla-button__button")]',
            # Selector por div contenedor
            '.d-flex.justify-content-center button',
            # XPath más genérico
            '//button[contains(text(), "Ver más")]'
        ]
        
        for selector in button_selectors:
            try:
                if selector.startswith("//") or selector.startswith("//*"):
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for button in buttons:
                    try:
                        # Verificar que el botón esté visible y habilitado
                        if button.is_displayed() and button.is_enabled():
                            # Obtener texto del botón de múltiples formas
                            button_text = (
                                button.get_attribute('text') or 
                                button.text or 
                                button.get_attribute('aria-label') or 
                                ""
                            ).lower()
                            
                            # Verificar que contiene el texto esperado
                            if any(phrase in button_text for phrase in ['ver más productos', 'ver más', 'más productos']):
                                # Scroll al botón primero
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                time.sleep(1.0)
                                
                                # Intentar click normal primero
                                try:
                                    button.click()
                                    time.sleep(3.0)  # Tiempo aumentado para cargar contenido
                                    return True
                                except:
                                    # Si falla, usar JavaScript click
                                    try:
                                        driver.execute_script("arguments[0].click();", button)
                                        time.sleep(3.0)
                                        return True
                                    except:
                                        # Si también falla, intentar click en elemento padre
                                        try:
                                            parent = button.find_element(By.XPATH, '..')
                                            parent.click()
                                            time.sleep(3.0)
                                            return True
                                        except:
                                            continue
                    except Exception as e:
                        continue
            except Exception as e:
                continue
        
        return False
    except Exception as e:
        print(f"Error en find_and_click_load_more_button: {e}")
        return False

def get_seller_cars(driver, seller_url, seller_name):
    """Extrae coches del vendedor - VERSION OPTIMIZADA"""
    print(f"\n{'=' * 60}")
    print(f"PROCESANDO VENDEDOR: {seller_name}")
    print(f"{'=' * 60}")
    
    cars_data = []
    
    try:
        driver.get(seller_url)
        time.sleep(0.8)
        
        # SCROLL INICIAL OPTIMIZADO
        print("Cargando pagina inicial...")
        for i in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.1)
        
        initial_links = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/item/')]"))
        print(f"Anuncios iniciales encontrados: {initial_links}")
        
        # CARGAR MAS ANUNCIOS - TIMING CORREGIDO PARA CARGAR TODOS
        total_buttons_clicked = 0
        consecutive_no_increase = 0
        print("Buscando mas anuncios...")
        
        for attempt in range(50):
            links_before = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/item/')]"))
            button_found = find_and_click_load_more_button(driver)
            
            if button_found:
                total_buttons_clicked += 1
                print(f"Boton 'Ver mas' #{total_buttons_clicked} clickeado")
                time.sleep(1.2)
                
                # Scroll adicional para forzar carga
                for i in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.2)
                
                links_after = len(driver.find_elements(By.XPATH, "//a[contains(@href, '/item/')]"))
                print(f"Anuncios despues del boton: {links_after}")
                
                if links_after <= links_before:
                    consecutive_no_increase += 1
                    print(f"Sin nuevos anuncios (intento {consecutive_no_increase}/3)")
                    if consecutive_no_increase >= 3:
                        print("No se encontraron mas anuncios despues de varios intentos")
                        break
                else:
                    consecutive_no_increase = 0
                    
            else:
                print("No se encontro boton 'Ver mas'")
                break
        
        # SCROLL FINAL OPTIMIZADO
        print("Scroll final para cargar todos los anuncios...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.05)
        
        # EXTRAER ENLACES
        car_links = []
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/item/')]")
        for link in links:
            href = link.get_attribute('href')
            if href and '/item/' in href:
                car_links.append(href)
        
        car_links = list(set(car_links))  # Eliminar duplicados
        
        print(f"TOTAL ANUNCIOS UNICOS ENCONTRADOS: {len(car_links)}")
        print("Iniciando extraccion de datos...")
        
        # PROCESAR CADA ANUNCIO
        if car_links:
            progress_bar = tqdm(car_links, desc=f"Extrayendo {seller_name}", colour="green", leave=False)
            for idx, car_url in enumerate(progress_bar):
                progress_bar.set_description(f"Extrayendo {seller_name} ({idx+1}/{len(car_links)})")
                car_data = extract_car_data(driver, car_url, seller_name)
                if car_data:
                    cars_data.append(car_data)
                time.sleep(0.1)
        
        print(f"\n{'=' * 60}")
        print(f"VENDEDOR COMPLETADO: {seller_name}")
        print(f"Coches extraidos exitosamente: {len(cars_data)}/{len(car_links)}")
        print(f"{'=' * 60}\n")
        
        return cars_data
        
    except Exception as e:
        print(f"ERROR en {seller_name}: {str(e)}")
        return cars_data

def main():
    """Funcion principal - OPTIMIZADA CON GOOGLE SHEETS"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 70)
        print("    WALLAPOP COCHES SCRAPER - VERSION AUTOMATIZADA")
        print("    Optimizada para velocidad y Google Sheets")
        print("=" * 70)
        
        # Obtener vendedores desde configuracion
        test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
        sellers = get_sellers(test_mode=test_mode)
        
        print(f"MODO: {'Testing' if test_mode else 'Produccion'}")
        print(f"VENDEDORES: {len(sellers)} configurados")
        
        driver = setup_browser()
        
        # Aceptar cookies optimizado
        try:
            driver.get("https://es.wallapop.com")
            time.sleep(1.5)
            cookie_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar')]"))
            )
            cookie_button.click()
            time.sleep(0.5)
        except:
            pass
        
        all_cars_data = []
        
        # PROCESAR VENDEDORES
        for seller_name, seller_url in sellers.items():
            try:
                seller_cars = get_seller_cars(driver, seller_url, seller_name)
                all_cars_data.extend(seller_cars)
                time.sleep(0.5)
            except Exception as e:
                print(f"ERROR en {seller_name}: {str(e)}")
                continue
        
        # GENERAR EXCEL LOCAL
        if all_cars_data:
            print(f"\n{'=' * 70}")
            print("RESUMEN FINAL")
            print(f"{'=' * 70}")
            print(f"Total coches extraidos: {len(all_cars_data)}")
            
            # Estadisticas de precios
            precios_contado_validos = [row['Precio al Contado'] for row in all_cars_data if row['Precio al Contado'] != 'No especificado']
            precios_financiado_validos = [row['Precio Financiado'] for row in all_cars_data if row['Precio Financiado'] != 'No especificado']
            
            print(f"Precios al contado extraidos: {len(precios_contado_validos)}/{len(all_cars_data)} ({len(precios_contado_validos)/len(all_cars_data)*100:.1f}%)")
            print(f"Precios financiados extraidos: {len(precios_financiado_validos)}/{len(all_cars_data)} ({len(precios_financiado_validos)/len(all_cars_data)*100:.1f}%)")
            
            print("Generando archivo Excel...")
            
            os.makedirs("../resultados", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"../resultados/coches_vendedores_AUTO_{timestamp}.xlsx"
            
            df = pd.DataFrame(all_cars_data)
            df_sorted = df.sort_values(['Vendedor', 'Marca', 'Modelo'])
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_sorted.to_excel(writer, sheet_name="Todos_los_Coches", index=False)
                
                for seller in df_sorted['Vendedor'].unique():
                    seller_df = df_sorted[df_sorted['Vendedor'] == seller]
                    sheet_name = seller.replace('.', '').replace(' ', '_')[:31]
                    seller_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                stats_data = []
                for seller in df_sorted['Vendedor'].unique():
                    seller_df = df_sorted[df_sorted['Vendedor'] == seller]
                    precios_contado_seller = len([p for p in seller_df['Precio al Contado'] if p != 'No especificado'])
                    stats_data.append({
                        'Vendedor': seller,
                        'Total_Coches': len(seller_df),
                        'Marcas_Diferentes': seller_df['Marca'].nunique(),
                        'Precios_Extraidos': precios_contado_seller,
                        'Porcentaje_Precios': f"{precios_contado_seller/len(seller_df)*100:.1f}%"
                    })
                
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name="Estadisticas", index=False)
            
            print(f"Excel generado exitosamente: {filename}")
            
            # SUBIR A GOOGLE SHEETS SI ESTA CONFIGURADO
            sheets_uploader = setup_google_sheets()
            if sheets_uploader:
                print("\nSUBIENDO A GOOGLE SHEETS...")
                success = sheets_uploader.upload_by_seller(df_sorted)
                if success:
                    print("EXITO: Datos subidos automaticamente a Google Sheets")
                else:
                    print("ERROR: Fallo al subir a Google Sheets")
            else:
                print("\nAVISO: Google Sheets no configurado - solo Excel local")
            
            print(f"{'=' * 70}")
        
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except Exception as e:
        print(f"\nERROR critico: {str(e)}")
    finally:
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()
