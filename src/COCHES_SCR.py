def detect_monthly_price(price_text, seller_name):
    """Detecta si un precio es mensual basado en el valor y vendedor - CORREGIDO"""
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
        print(f"  [DEBUG] Error en detect_monthly_price: {e}, texto: '{price_text}'")
        return price_text if price_text else "No especificado"

def extract_car_data(driver, url, seller_name):
    """Extrae datos del coche - VERSION CORREGIDA PARA PRECIOS MULTIPLES"""
    try:
        driver.get(url)
        time.sleep(1.5)  # Tiempo aumentado para carga de precios
        
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
        
        # PRECIOS - EXTRACCION CORREGIDA CON MEJOR DEBUGGING
        precio_contado = "No especificado"
        precio_financiado = "No especificado"
        
        # ESPERAR A QUE CARGUEN LOS PRECIOS EXPLICITAMENTE
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '€')]"))
            )
            print(f"  [DEBUG] Elementos con € encontrados en la página")
        except:
            print(f"  [DEBUG] No se encontraron elementos con € después de 5 segundos")
            pass
        
        # ESTRATEGIA MEJORADA: BUSCAR PRECIOS POR ETIQUETAS PRIMERO
        print(f"  [DEBUG] Iniciando extracción de precios para {seller_name}")
        
        # 1. BUSCAR PRECIO AL CONTADO POR ETIQUETA
        try:
            # Buscar por el label "Precio al contado" y luego el span con el precio
            contado_elements = driver.find_elements(By.XPATH, 
                "//span[text()='Precio al contado']/following::span[contains(@class, 'ItemDetailPrice') and contains(text(), '€')]"
            )
            
            if contado_elements:
                raw_price = contado_elements[0].text.strip()
                print(f"  [DEBUG] Precio al contado encontrado por etiqueta: '{raw_price}'")
                precio_contado = detect_monthly_price(raw_price, seller_name)
            else:
                print(f"  [DEBUG] No se encontró precio al contado por etiqueta")
        except Exception as e:
            print(f"  [DEBUG] Error buscando precio al contado por etiqueta: {e}")
        
        # 2. BUSCAR PRECIO FINANCIADO POR ETIQUETA
        try:
            financiado_elements = driver.find_elements(By.XPATH, 
                "//span[text()='Precio financiado']/following::span[contains(@class, 'ItemDetailPrice') and contains(text(), '€')]"
            )
            
            if financiado_elements:
                raw_price = financiado_elements[0].text.strip()
                print(f"  [DEBUG] Precio financiado encontrado por etiqueta: '{raw_price}'")
                precio_financiado = detect_monthly_price(raw_price, seller_name)
            else:
                print(f"  [DEBUG] No se encontró precio financiado por etiqueta")
        except Exception as e:
            print(f"  [DEBUG] Error buscando precio financiado por etiqueta: {e}")
        
        # 3. FALLBACK: USAR SELECTORES CSS ESPECÍFICOS SI NO ENCUENTRA POR ETIQUETAS
        if precio_contado == "No especificado":
            print(f"  [DEBUG] Probando selectores CSS para precio al contado")
            
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
                            print(f"  [DEBUG] Precio contado CSS encontrado: '{text}' con selector: {selector}")
                            precio_contado = detect_monthly_price(text, seller_name)
                            break
                    if precio_contado != "No especificado":
                        break
                except Exception as e:
                    print(f"  [DEBUG] Error con selector CSS contado {selector}: {e}")
                    continue
        
        if precio_financiado == "No especificado":
            print(f"  [DEBUG] Probando selectores CSS para precio financiado")
            
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
                            print(f"  [DEBUG] Precio financiado CSS encontrado: '{text}' con selector: {selector}")
                            precio_financiado = detect_monthly_price(text, seller_name)
                            break
                    if precio_financiado != "No especificado":
                        break
                except Exception as e:
                    print(f"  [DEBUG] Error con selector CSS financiado {selector}: {e}")
                    continue
        
        # 4. ÚLTIMO FALLBACK: BUSCAR CUALQUIER PRECIO SI NO TIENE PRECIO AL CONTADO
        if precio_contado == "No especificado":
            print(f"  [DEBUG] Usando último fallback para encontrar precios")
            try:
                price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
                print(f"  [DEBUG] Encontrados {len(price_elements)} elementos con €")
                
                valid_prices = []
                for i, elem in enumerate(price_elements[:10]):  # Limitar a 10 elementos
                    try:
                        text = elem.text.strip().replace('&nbsp;', ' ').replace('\xa0', ' ')
                        if not text:
                            continue
                            
                        print(f"  [DEBUG] Elemento {i}: '{text}'")
                        
                        # REGEX PARA CAPTURAR PRECIOS REALISTAS
                        price_patterns = [
                            r'(\d{1,3}(?:\.\d{3})+)\s*€',  # 15.000€ (con puntos)
                            r'(\d{1,6})\s*€'               # 15000€ o 300€ (sin puntos, 1-6 dígitos)
                        ]
                        
                        for pattern in price_patterns:
                            price_matches = re.findall(pattern, text)
                            for price_match in price_matches:
                                try:
                                    price_clean = price_match.replace('.', '')
                                    price_value = int(price_clean)
                                    
                                    # RANGO AMPLIADO: 50€ hasta 300.000€
                                    if 50 <= price_value <= 300000:
                                        formatted_price = f"{price_value:,}".replace(',', '.') + " €" if price_value >= 1000 else f"{price_value} €"
                                        final_price = detect_monthly_price(formatted_price, seller_name)
                                        valid_prices.append((price_value, final_price, text))
                                        print(f"  [DEBUG] Precio válido encontrado: {price_value} -> {final_price}")
                                except Exception as ex:
                                    print(f"  [DEBUG] Error procesando precio {price_match}: {ex}")
                                    continue
                    except Exception as ex:
                        print(f"  [DEBUG] Error procesando elemento {i}: {ex}")
                        continue
                
                # Tomar el precio más alto como precio al contado
                if valid_prices:
                    valid_prices = sorted(set(valid_prices), key=lambda x: x[0], reverse=True)
                    precio_contado = valid_prices[0][1]
                    print(f"  [DEBUG] Precio final seleccionado: {precio_contado}")
                else:
                    print(f"  [DEBUG] No se encontraron precios válidos en el fallback")
                        
            except Exception as e:
                print(f"  [DEBUG] Error en último fallback de precios: {e}")
        
        # MOSTRAR RESULTADO FINAL DE PRECIOS
        print(f"  [DEBUG] RESULTADO FINAL - Contado: '{precio_contado}', Financiado: '{precio_financiado}'")
        
        # CARACTERISTICAS - SELECTOR VERIFICADO
        attributes = extract_car_attributes(driver)
        
        # DATOS ADICIONALES DEL HTML
        main_data = extract_main_car_info_from_html(driver)
        
        # EXTRAER MARCA Y MODELO COMPLETO DEL TITULO
        marca, modelo_completo = extract_brand_and_full_model_from_title(title)
        
        # Logging visual con informacion de errores
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
