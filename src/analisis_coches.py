"""

Analizador Historico Coches - Version Google Sheets V1.4 ORDEN MARCA ALFABÉTICO
Lee datos del scraper desde Google Sheets y actualiza el historico evolutivo de precios

"""

import sys
import os
import time
import pandas as pd
import re
import hashlib
from datetime import datetime, timedelta
import numpy as np

# Importar modulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_sellers
from google_sheets_uploader import GoogleSheetsUploader

class AnalizadorHistoricoCoches:
    def __init__(self):
        self.tiempo_inicio = datetime.now()
        
        # Variables de fecha
        self.fecha_actual = None
        self.fecha_str = None
        self.fecha_display = None
        
        # Estadisticas de procesamiento
        self.stats = {
            'total_archivo_nuevo': 0,
            'total_historico': 0,
            'coches_nuevos': 0,
            'coches_actualizados': 0,
            'coches_vendidos': 0,
            'errores': 0,
            'tiempo_ejecucion': 0
        }
        
        # Listas para tracking
        self.coches_nuevos_lista = []
        self.coches_vendidos_lista = []
        self.cambios_precio = []
        
        # Google Sheets handler
        self.gs_handler = None
        
        # ID del sheet para historico (usar el mismo que el scraper)
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        
    def inicializar_google_sheets(self):
        """Inicializa la conexion a Google Sheets"""
        try:
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            
            if not credentials_json:
                # Para testing local
                credentials_file = "../credentials/service-account.json"
                if os.path.exists(credentials_file):
                    self.gs_handler = GoogleSheetsUploader(
                        credentials_file=credentials_file,
                        sheet_id=self.sheet_id
                    )
                else:
                    raise Exception("No se encontraron credenciales locales")
            else:
                # Para GitHub Actions
                self.gs_handler = GoogleSheetsUploader(
                    credentials_json_string=credentials_json,
                    sheet_id=self.sheet_id
                )
            
            # Probar conexion
            if not self.gs_handler.test_connection():
                raise Exception("No se pudo conectar a Google Sheets")
            
            print("CONEXION: Google Sheets inicializada correctamente")
            return True
            
        except Exception as e:
            print(f"ERROR INICIALIZACION: {str(e)}")
            return False
    
    def crear_id_unico_coche(self, fila):
        """
        Crea ID unico basado en: URL (principalmente)
        URL es unica para cada coche en Wallapop
        """
        try:
            url = str(fila.get('URL', '')).strip()
            if url and url != 'No especificado':
                return hashlib.md5(url.encode()).hexdigest()[:12]
            
            # Fallback con otros datos si URL no disponible
            vendedor = str(fila.get('Vendedor', '')).strip()
            marca = str(fila.get('Marca', '')).strip()
            modelo = str(fila.get('Modelo', '')).strip()
            km = str(fila.get('KM', '')).strip()
            
            clave_fallback = f"{vendedor}_{marca}_{modelo}_{km}"
            return hashlib.md5(clave_fallback.encode()).hexdigest()[:12]
            
        except Exception as e:
            # Ultimo recurso
            return hashlib.md5(f"{time.time()}".encode()).hexdigest()[:12]
    
    def extraer_fecha_de_datos(self, df_nuevo):
        """Extrae la fecha de los datos del scraper"""
        try:
            if 'Fecha_Extraccion' in df_nuevo.columns:
                fecha_str = df_nuevo['Fecha_Extraccion'].iloc[0]
                if isinstance(fecha_str, str) and '/' in fecha_str:
                    fecha_parte = fecha_str.split(' ')[0]  # Quitar hora si existe
                    fecha_obj = datetime.strptime(fecha_parte, "%d/%m/%Y")
                    return fecha_obj, fecha_parte
            
            # Fallback: usar fecha actual
            fecha_actual = datetime.now()
            fecha_display = fecha_actual.strftime("%d/%m/%Y")
            print(f"ADVERTENCIA: Usando fecha actual {fecha_display}")
            return fecha_actual, fecha_display
            
        except Exception as e:
            print(f"ADVERTENCIA: Error extrayendo fecha: {e}, usando fecha actual")
            fecha_actual = datetime.now()
            return fecha_actual, fecha_actual.strftime("%d/%m/%Y")
    
    def mostrar_header(self):
        """Muestra el header del sistema"""
        print("="*80)
        print("ANALIZADOR HISTORICO COCHES V1.4 - ORDEN MARCA ALFABÉTICO")
        print("="*80)
        print(f"Fecha procesamiento: {self.fecha_display}")
        print("Logica: URL como identificador unico principal")
        print("Fuente: Google Sheets (Une SCR-J1 y SCR-J2)")
        print("Destino: Hoja Data_Historico")
        print("Precio: SOLO precio al contado (columnas Precio_FECHA)")
        print("Orden: Datos básicos -> Características -> Control -> PRECIOS AL FINAL")
        print("CORRECCION V1.4: Fix error JSON + Orden por Vendedor->Marca alfabética")
        print("Ordenacion: Vendedor (A-Z) -> Marca alfabética (A-Z)")
        print()
    
    def leer_datos_scraper_unificados(self):
        """Lee y unifica datos de ambos jobs del scraper"""
        try:
            print("Leyendo datos de jobs del scraper...")
            
            # Usar fecha actual para buscar hojas
            fecha_hoy = datetime.now()
            fecha_str_corta = fecha_hoy.strftime("%d/%m/%y")
            
            sheet_j1 = f"SCR-J1 {fecha_str_corta}"
            sheet_j2 = f"SCR-J2 {fecha_str_corta}"
            
            print(f"Buscando hojas: {sheet_j1} y {sheet_j2}")
            
            # Abrir spreadsheet
            spreadsheet = self.gs_handler.client.open_by_key(self.sheet_id)
            
            # Listar todas las hojas para debug
            todas_las_hojas = [ws.title for ws in spreadsheet.worksheets()]
            hojas_scr = [h for h in todas_las_hojas if h.startswith('SCR')]
            print(f"Hojas SCR disponibles: {hojas_scr}")
            
            # Intentar leer ambas hojas
            df_j1 = None
            df_j2 = None
            
            try:
                worksheet_j1 = spreadsheet.worksheet(sheet_j1)
                data_j1 = worksheet_j1.get_all_records()
                if data_j1:
                    df_j1 = pd.DataFrame(data_j1)
                    print(f"Hoja {sheet_j1}: {len(df_j1)} coches")
            except Exception as e:
                print(f"No se pudo leer {sheet_j1}: {e}")
            
            try:
                worksheet_j2 = spreadsheet.worksheet(sheet_j2)
                data_j2 = worksheet_j2.get_all_records()
                if data_j2:
                    df_j2 = pd.DataFrame(data_j2)
                    print(f"Hoja {sheet_j2}: {len(df_j2)} coches")
            except Exception as e:
                print(f"No se pudo leer {sheet_j2}: {e}")
            
            # Unificar dataframes
            dfs_a_unir = []
            if df_j1 is not None and not df_j1.empty:
                dfs_a_unir.append(df_j1)
            if df_j2 is not None and not df_j2.empty:
                dfs_a_unir.append(df_j2)
            
            if not dfs_a_unir:
                raise Exception("No se encontraron datos en ninguna hoja del scraper")
            
            # Unir todos los dataframes
            df_unificado = pd.concat(dfs_a_unir, ignore_index=True)
            print(f"DATOS UNIFICADOS: {len(df_unificado)} coches totales")
            
            # Debug: mostrar columnas encontradas
            print(f"Columnas encontradas: {list(df_unificado.columns)}")
            
            # Validar estructura
            df_unificado = self.validar_estructura_archivo(df_unificado)
            
            # Crear ID unico para cada coche
            df_unificado['ID_Unico_Coche'] = df_unificado.apply(self.crear_id_unico_coche, axis=1)
            
            # Limpiar precios y kilometraje (SOLO INTERNAMENTE)
            df_unificado = self.limpiar_datos_numericos(df_unificado)
            
            self.stats['total_archivo_nuevo'] = len(df_unificado)
            print(f"Coches procesados: {self.stats['total_archivo_nuevo']:,}")
            
            # Extraer fecha
            self.fecha_actual, self.fecha_display = self.extraer_fecha_de_datos(df_unificado)
            self.fecha_str = self.fecha_actual.strftime("%Y%m%d")
            
            return df_unificado
            
        except Exception as e:
            print(f"ERROR leyendo datos del scraper: {str(e)}")
            raise
    
    def validar_estructura_archivo(self, df):
        """Valida y transforma columnas del scraper al formato del histórico"""
        print(f"Validando y transformando columnas del scraper...")
        
        # TRANSFORMACIÓN COMPLETA: Scraper → Histórico
        mapeo_columnas = {
            # Transformaciones necesarias
            'Precio al Contado': 'Precio_Contado',      # Para procesamiento interno
            'Año': 'Ano',                               # Año → Ano
            'Nº Plazas': 'Plazas',                      # Nº Plazas → Plazas  
            'Nº Puertas': 'Puertas',                    # Nº Puertas → Puertas
            'Conducción': 'Conduccion',                 # Conducción → Conduccion (sin acento)
            'Fecha Extracción': 'Fecha_Extraccion'      # Para eliminar después
        }
        
        print(f"Columnas originales: {list(df.columns)}")
        df = df.rename(columns=mapeo_columnas)
        print(f"Columnas transformadas: {list(df.columns)}")
        
        # Columnas criticas
        columnas_minimas = ['Marca', 'Modelo', 'Vendedor', 'URL']
        columnas_faltantes = [col for col in columnas_minimas if col not in df.columns]
        
        if columnas_faltantes:
            print(f"COLUMNAS DISPONIBLES: {list(df.columns)}")
            raise ValueError(f"Columnas criticas faltantes: {columnas_faltantes}")
        
        # Agregar columnas faltantes con valores por defecto
        columnas_deseadas = {
            'Precio_Contado': 'No especificado',
            'KM': 'No especificado',
            'Ano': 'No especificado'
        }
        
        for col, valor_default in columnas_deseadas.items():
            if col not in df.columns:
                df[col] = valor_default
                print(f"Columna '{col}' anadida con valor por defecto")
        
        # Limpiar URLs vacias
        urls_vacias = df['URL'].isnull().sum() + (df['URL'] == 'No especificado').sum()
        if urls_vacias > 0:
            print(f"ADVERTENCIA: {urls_vacias} coches con URL vacia seran ignoradas")
            df = df[df['URL'].notna()]
            df = df[df['URL'] != 'No especificado']
            df = df[df['URL'] != '']
        
        return df
    
    def limpiar_datos_numericos(self, df):
        """Limpia y convierte datos numericos (SOLO PARA USO INTERNO)"""
        try:
            print("Limpiando datos numericos (uso interno)...")
            
            # Limpiar kilometraje
            if 'KM' in df.columns:
                def limpiar_km(km_text):
                    if pd.isna(km_text) or km_text == 'No especificado':
                        return 0
                    # Extraer numeros del texto
                    numeros = re.findall(r'\d+', str(km_text).replace('.', '').replace(',', ''))
                    if numeros:
                        return int(''.join(numeros))
                    return 0
                
                df['KM_Numerico_Internal'] = df['KM'].apply(limpiar_km)
            
            # Limpiar año
            if 'Ano' in df.columns:
                def limpiar_ano(ano_text):
                    if pd.isna(ano_text) or ano_text == 'No especificado':
                        return 0
                    numeros = re.findall(r'\d{4}', str(ano_text))
                    if numeros:
                        ano = int(numeros[0])
                        if 1990 <= ano <= datetime.now().year + 1:
                            return ano
                    return 0
                
                df['Ano_Numerico_Internal'] = df['Ano'].apply(limpiar_ano)
            
            return df
            
        except Exception as e:
            print(f"ADVERTENCIA: Error limpiando datos: {str(e)}")
            return df
    
    def obtener_columnas_precios_fechas(self, df):
        """Obtiene las columnas de precios por fecha del historico"""
        columnas_precios = [col for col in df.columns if col.startswith('Precio_') and not col.endswith('_Internal')]
        columnas_precios.sort()
        return columnas_precios
    
    def obtener_fecha_anterior(self, columnas_fechas):
        """Obtiene la fecha anterior mas reciente de las columnas"""
        if not columnas_fechas:
            return None
        
        fechas = []
        for col in columnas_fechas:
            try:
                fecha_str = col.replace('Precio_', '')  # Quitar prefijo
                fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
                if fecha_obj.strftime("%d/%m/%Y") != self.fecha_display:
                    fechas.append(fecha_obj)
            except:
                continue
        
        if fechas:
            return max(fechas).strftime("%d/%m/%Y")
        return None
    
    def leer_historico_existente(self):
        """Lee el historico existente desde Google Sheets - V1.4 CORREGIDO"""
        try:
            print("Intentando leer historico existente...")
            
            # Abrir spreadsheet
            spreadsheet = self.gs_handler.client.open_by_key(self.sheet_id)
            
            try:
                worksheet_historico = spreadsheet.worksheet("Data_Historico")
                data_historico = worksheet_historico.get_all_records()
                
                if not data_historico:
                    print("Hoja Data_Historico existe pero esta vacia")
                    return None
                
                df_historico = pd.DataFrame(data_historico)
                print(f"Historico leido: {len(df_historico)} coches")
                
                # Verificar columnas necesarias
                if 'URL' not in df_historico.columns:
                    raise Exception("Columna URL faltante en historico")
                
                # CORRECCION V1.4: REGENERAR columnas internas para ordenamiento
                print("V1.4: Regenerando columnas numericas internas...")
                
                # Regenerar KM_Numerico_Internal (aunque no se use para ordenar)
                if 'KM' in df_historico.columns:
                    df_historico['KM_Numerico_Internal'] = df_historico['KM'].apply(self.limpiar_km_interno_seguro)
                else:
                    df_historico['KM_Numerico_Internal'] = 0
                
                # Regenerar Ano_Numerico_Internal 
                if 'Ano' in df_historico.columns:
                    df_historico['Ano_Numerico_Internal'] = df_historico['Ano'].apply(self.limpiar_ano_interno_seguro)
                else:
                    df_historico['Ano_Numerico_Internal'] = 0
                
                # LIMPIEZA PROACTIVA DE VALORES PROBLEMÁTICOS
                df_historico = self.limpiar_valores_problematicos_lectura(df_historico)
                
                self.stats['total_historico'] = len(df_historico)
                print(f"V1.4: Historico regenerado con columnas internas")
                return df_historico
                
            except Exception as e:
                if "not found" in str(e).lower() or "worksheet not found" in str(e).lower():
                    print("Hoja Data_Historico no existe - sera creada")
                    return None
                else:
                    raise e
                    
        except Exception as e:
            print(f"ERROR leyendo historico: {str(e)}")
            raise
    
    def limpiar_valores_problematicos_lectura(self, df):
        """V1.4: Limpia valores problemáticos al leer el histórico"""
        try:
            print("V1.4: Limpiando valores problemáticos del histórico...")
            
            # Reemplazar strings problemáticos
            df = df.replace(['nan', 'NaN', 'None', 'null', ''], np.nan)
            
            # Limpiar infinitos y valores extremos
            for column in df.columns:
                if df[column].dtype in ['float64', 'int64', 'float32', 'int32']:
                    # Reemplazar infinitos
                    df[column] = df[column].replace([np.inf, -np.inf], np.nan)
                    # Rellenar NaN con 0
                    df[column] = df[column].fillna(0)
                    # Limitar valores extremos
                    df[column] = df[column].clip(-1e10, 1e10)
                elif df[column].dtype == 'object':
                    # Para strings, reemplazar NaN con string vacío
                    df[column] = df[column].fillna('')
                    # Asegurar que son strings
                    df[column] = df[column].astype(str)
            
            print("V1.4: Valores problemáticos limpiados")
            return df
            
        except Exception as e:
            print(f"ADVERTENCIA V1.4: Error limpiando valores: {e}")
            return df
    
    def limpiar_km_interno_seguro(self, km_text):
        """V1.4: Función auxiliar SEGURA para limpiar KM"""
        try:
            if pd.isna(km_text) or km_text == 'No especificado' or km_text == '' or km_text == 'nan':
                return 0
            
            km_str = str(km_text).replace('.', '').replace(',', '').replace(' ', '')
            numeros = re.findall(r'\d+', km_str)
            if numeros:
                km_val = int(''.join(numeros))
                # Limitar a rango razonable
                return max(0, min(km_val, 999999))
            return 0
        except:
            return 0
    
    def limpiar_ano_interno_seguro(self, ano_text):
        """V1.4: Función auxiliar SEGURA para limpiar año"""
        try:
            if pd.isna(ano_text) or ano_text == 'No especificado' or ano_text == '' or ano_text == 'nan':
                return 0
            
            ano_str = str(ano_text)
            numeros = re.findall(r'\d{4}', ano_str)
            if numeros:
                ano = int(numeros[0])
                if 1990 <= ano <= datetime.now().year + 1:
                    return ano
            return 0
        except:
            return 0
    
    def limpiar_km_interno(self, km_text):
        """Funcion auxiliar para limpiar KM"""
        return self.limpiar_km_interno_seguro(km_text)
    
    def limpiar_ano_interno(self, ano_text):
        """Funcion auxiliar para limpiar año"""
        return self.limpiar_ano_interno_seguro(ano_text)
    
    def primera_ejecucion(self, df_nuevo):
        """Crea el historico por primera vez"""
        print("Primera ejecucion - Creando historico inicial")
        
        df_historico = df_nuevo.copy()
        
        # Columnas de control
        df_historico['Primera_Deteccion'] = self.fecha_display
        df_historico['Estado'] = 'activo'
        df_historico['Fecha_Venta'] = ''  # V1.4: String vacío en lugar de pd.NA
        
        # Columna de precio para la fecha actual
        col_precio_hoy = f"Precio_{self.fecha_display}"
        df_historico[col_precio_hoy] = df_historico['Precio_Contado']
        
        # Asegurar que existen columnas internas ANTES del ordenamiento
        if 'KM_Numerico_Internal' not in df_historico.columns:
            df_historico['KM_Numerico_Internal'] = df_historico['KM'].apply(self.limpiar_km_interno_seguro)
        if 'Ano_Numerico_Internal' not in df_historico.columns:
            df_historico['Ano_Numerico_Internal'] = df_historico['Ano'].apply(self.limpiar_ano_interno_seguro)
        
        # V1.4: Limpiar valores problemáticos ANTES de ordenar
        df_historico = self.limpiar_valores_problematicos_lectura(df_historico)
        
        # Ordenar ANTES de eliminar columnas
        df_historico = self.ordenar_dataframe_seguro(df_historico)
        
        self.stats['total_historico'] = len(df_historico)
        self.stats['coches_nuevos'] = len(df_historico)
        self.coches_nuevos_lista = df_historico[['Marca', 'Modelo', 'Vendedor']].to_dict('records')
        
        return df_historico
    
    def procesar_coches_nuevos_y_existentes(self, df_nuevo, df_historico):
        """Procesa coches nuevos y actualiza existentes - V1.4 CORREGIDO"""
        try:
            print("Procesando cambios en el inventario...")
            
            col_precio_hoy = f"Precio_{self.fecha_display}"
            print(f"Anadiendo columna: {col_precio_hoy}")
            
            # Obtener columnas existentes de precios
            columnas_precios = self.obtener_columnas_precios_fechas(df_historico)
            fecha_anterior = self.obtener_fecha_anterior(columnas_precios)
            
            if fecha_anterior:
                print(f"Comparando con fecha anterior: {fecha_anterior}")
            
            # URLs como identificador principal
            urls_historico = set(df_historico['URL'].values)
            urls_nuevos = set(df_nuevo['URL'].values)
            
            coches_nuevos_urls = urls_nuevos - urls_historico
            coches_existentes_urls = urls_nuevos & urls_historico
            coches_vendidos_urls = urls_historico - urls_nuevos
            
            print(f"Analisis de cambios:")
            print(f"    - Nuevos: {len(coches_nuevos_urls)}")
            print(f"    - Existentes: {len(coches_existentes_urls)}")
            print(f"    - Posibles ventas: {len(coches_vendidos_urls)}")
            
            # Preparar dataframe actualizado
            df_actualizado = df_historico.copy()
            df_actualizado[col_precio_hoy] = ''  # V1.4: String vacío en lugar de pd.NA
            
            # PROCESAR COCHES EXISTENTES
            for url_coche in coches_existentes_urls:
                try:
                    fila_nueva = df_nuevo[df_nuevo['URL'] == url_coche].iloc[0]
                    precio_nuevo = str(fila_nueva['Precio_Contado'])  # V1.4: Convertir a string
                    
                    mask = df_actualizado['URL'] == url_coche
                    df_actualizado.loc[mask, col_precio_hoy] = precio_nuevo
                    df_actualizado.loc[mask, 'Estado'] = 'activo'
                    
                    # Detectar cambios de precio
                    if fecha_anterior:
                        col_precio_anterior = f"Precio_{fecha_anterior}"
                        if col_precio_anterior in df_actualizado.columns:
                            precio_anterior = df_actualizado.loc[mask, col_precio_anterior].iloc[0]
                            if precio_anterior and str(precio_anterior) != precio_nuevo:
                                self.cambios_precio.append({
                                    'Marca': fila_nueva['Marca'],
                                    'Modelo': fila_nueva['Modelo'],
                                    'Vendedor': fila_nueva['Vendedor'],
                                    'Precio_Anterior': precio_anterior,
                                    'Precio_Nuevo': precio_nuevo
                                })
                    
                    self.stats['coches_actualizados'] += 1
                    
                except Exception as e:
                    self.stats['errores'] += 1
                    print(f"Error procesando coche existente: {str(e)}")
                    continue
            
            # PROCESAR COCHES VENDIDOS
            for url_coche in coches_vendidos_urls:
                try:
                    mask = df_actualizado['URL'] == url_coche
                    if mask.any():
                        estado_actual = df_actualizado.loc[mask, 'Estado'].iloc[0]
                        
                        if estado_actual == 'activo':
                            df_actualizado.loc[mask, 'Estado'] = 'vendido'
                            df_actualizado.loc[mask, 'Fecha_Venta'] = self.fecha_display
                            
                            fila_vendida = df_actualizado.loc[mask].iloc[0]
                            self.coches_vendidos_lista.append({
                                'Marca': fila_vendida['Marca'],
                                'Modelo': fila_vendida['Modelo'], 
                                'Vendedor': fila_vendida['Vendedor']
                            })
                            
                            self.stats['coches_vendidos'] += 1
                            
                except Exception as e:
                    print(f"Error procesando coche vendido: {str(e)}")
                    continue
            
            # PROCESAR COCHES NUEVOS
            for url_nueva in coches_nuevos_urls:
                try:
                    fila_nueva = df_nuevo[df_nuevo['URL'] == url_nueva].iloc[0]
                    
                    nueva_fila = {
                        'ID_Unico_Coche': fila_nueva['ID_Unico_Coche'],
                        'Marca': str(fila_nueva['Marca']) if pd.notna(fila_nueva['Marca']) else 'No especificado',
                        'Modelo': str(fila_nueva['Modelo']) if pd.notna(fila_nueva['Modelo']) else 'No especificado',
                        'Vendedor': str(fila_nueva['Vendedor']) if pd.notna(fila_nueva['Vendedor']) else 'No especificado',
                        'Ano': str(fila_nueva['Ano']) if pd.notna(fila_nueva['Ano']) else 'No especificado',
                        'KM': str(fila_nueva['KM']) if pd.notna(fila_nueva['KM']) else 'No especificado',
                        'URL': str(fila_nueva['URL']),
                        'Primera_Deteccion': self.fecha_display,
                        'Estado': 'activo',
                        'Fecha_Venta': ''  # V1.4: String vacío
                    }
                    
                    # Anadir caracteristicas del coche con nombres transformados
                    caracteristicas_coche = ['Tipo', 'Plazas', 'Puertas', 'Combustible', 'Potencia', 'Conduccion']
                    for caracteristica in caracteristicas_coche:
                        if caracteristica in fila_nueva:
                            nueva_fila[caracteristica] = str(fila_nueva[caracteristica]) if pd.notna(fila_nueva[caracteristica]) else 'No especificado'
                    
                    # Inicializar todas las columnas de precios anteriores con string vacío
                    for col_precio in columnas_precios:
                        nueva_fila[col_precio] = ''
                    
                    # Anadir precio para la fecha actual
                    nueva_fila[col_precio_hoy] = str(fila_nueva['Precio_Contado'])
                    
                    # Crear columnas internas para ordenamiento (NO se guardaran en sheets)
                    nueva_fila['KM_Numerico_Internal'] = fila_nueva.get('KM_Numerico_Internal', 0)
                    nueva_fila['Ano_Numerico_Internal'] = fila_nueva.get('Ano_Numerico_Internal', 0)
                    
                    df_actualizado = pd.concat([df_actualizado, pd.DataFrame([nueva_fila])], ignore_index=True)
                    
                    self.stats['coches_nuevos'] += 1
                    self.coches_nuevos_lista.append({
                        'Marca': nueva_fila['Marca'],
                        'Modelo': nueva_fila['Modelo'],
                        'Vendedor': nueva_fila['Vendedor']
                    })
                    
                except Exception as e:
                    self.stats['errores'] += 1
                    print(f"Error procesando coche nuevo: {str(e)}")
                    continue
            
            # V1.4: Regenerar columnas internas para TODOS los coches
            print("V1.4: Regenerando columnas internas para todos los coches...")
            df_actualizado['KM_Numerico_Internal'] = df_actualizado['KM'].apply(self.limpiar_km_interno_seguro)
            df_actualizado['Ano_Numerico_Internal'] = df_actualizado['Ano'].apply(self.limpiar_ano_interno_seguro)
            
            # V1.4: Limpiar valores problemáticos
            df_actualizado = self.limpiar_valores_problematicos_lectura(df_actualizado)
            
            # Ordenar resultado final con función segura
            df_actualizado = self.ordenar_dataframe_seguro(df_actualizado)
            
            return df_actualizado
            
        except Exception as e:
            print(f"ERROR critico en procesamiento: {str(e)}")
            raise
    
    def ordenar_dataframe_seguro(self, df):
        """V1.4: Ordena por Vendedor (A-Z) -> Marca alfabética (A-Z)"""
        try:
            print("V1.4: Ordenando por Vendedor y Marca alfabética...")
            
            # Asegurar que la columna Marca existe y es string
            if 'Marca' not in df.columns:
                df['Marca'] = 'No especificado'
            
            # Convertir Marca a string y limpiar para ordenamiento
            df['Marca'] = df['Marca'].astype(str).fillna('No especificado')
            
            # Separar coches activos y vendidos
            df_activos = df[df['Estado'] == 'activo'].copy()
            df_vendidos = df[df['Estado'] == 'vendido'].copy()
            
            # Ordenar activos por Vendedor (A-Z) y luego por Marca (A-Z)
            if not df_activos.empty:
                try:
                    df_activos = df_activos.sort_values(
                        ['Vendedor', 'Marca'], 
                        ascending=[True, True],  # Ambos alfabéticos A-Z
                        na_position='last'
                    )
                    print(f"V1.4: {len(df_activos)} coches activos ordenados por Vendedor->Marca")
                except Exception as e:
                    print(f"ADVERTENCIA: Error ordenando activos: {e}")
            
            # Ordenar vendidos por fecha de venta
            if not df_vendidos.empty and 'Fecha_Venta' in df_vendidos.columns:
                try:
                    df_vendidos = df_vendidos.sort_values(
                        'Fecha_Venta', 
                        ascending=False,
                        na_position='last'
                    )
                    print(f"V1.4: {len(df_vendidos)} coches vendidos ordenados por fecha")
                except Exception as e:
                    print(f"ADVERTENCIA: Error ordenando vendidos: {e}")
            
            # Concatenar: activos arriba, vendidos abajo
            df_ordenado = pd.concat([df_activos, df_vendidos], ignore_index=True)
            
            print("V1.4: Ordenamiento completado - Vendedor (A-Z) -> Marca (A-Z)")
            return df_ordenado
            
        except Exception as e:
            print(f"ADVERTENCIA V1.4: Error ordenando datos: {str(e)}")
            return df
    
    def preparar_dataframe_para_sheets(self, df_historico):
        """V1.4: Prepara el dataframe con limpieza EXHAUSTIVA para Google Sheets"""
        print("V1.4: Preparando datos para Google Sheets con limpieza exhaustiva...")
        
        df_sheets = df_historico.copy()
        
        # PASO 1: ELIMINAR COLUMNAS NO DESEADAS
        columnas_a_eliminar = [
            'KM_Numerico_Internal',
            'Ano_Numerico_Internal',
            'Precio_Contado',
            'Precio Financiado',
            'Fecha_Extraccion'
        ]
        
        columnas_eliminadas = [col for col in columnas_a_eliminar if col in df_sheets.columns]
        if columnas_eliminadas:
            df_sheets = df_sheets.drop(columnas_eliminadas, axis=1)
            print(f"V1.4: Columnas eliminadas: {columnas_eliminadas}")
        
        # PASO 2: LIMPIEZA EXHAUSTIVA DE VALORES PROBLEMÁTICOS
        print("V1.4: Aplicando limpieza exhaustiva...")
        
        # Reemplazar infinitos y NaN
        df_sheets = df_sheets.replace([np.inf, -np.inf], np.nan)
        
        # Procesar cada columna según su tipo
        for column in df_sheets.columns:
            if df_sheets[column].dtype in ['float64', 'int64', 'float32', 'int32']:
                # Para columnas numéricas
                df_sheets[column] = pd.to_numeric(df_sheets[column], errors='coerce')
                df_sheets[column] = df_sheets[column].fillna(0)
                df_sheets[column] = df_sheets[column].clip(-1e10, 1e10)
                # Convertir a int si son enteros para evitar problemas de float
                if df_sheets[column].notna().all() and (df_sheets[column] % 1 == 0).all():
                    df_sheets[column] = df_sheets[column].astype(int)
            else:
                # Para columnas de texto
                df_sheets[column] = df_sheets[column].fillna('')
                df_sheets[column] = df_sheets[column].astype(str)
                df_sheets[column] = df_sheets[column].replace(['nan', 'None', 'NaN', 'null'], '')
        
        # PASO 3: ORDEN FINAL CON NOMBRES TRANSFORMADOS
        print("V1.4: Aplicando orden con precios al final...")
        
        orden_basico = [
            'ID_Unico_Coche', 'Marca', 'Modelo', 'Vendedor', 'Ano', 'KM',
            'Tipo', 'Plazas', 'Puertas', 'Combustible', 'Potencia', 'Conduccion',
            'URL', 'Primera_Deteccion', 'Estado', 'Fecha_Venta'
        ]
        
        # Obtener columnas de precios ordenadas cronológicamente
        columnas_precios = [col for col in df_sheets.columns if col.startswith('Precio_')]
        def ordenar_fecha_precio(col_precio):
            try:
                fecha_str = col_precio.replace('Precio_', '')
                return datetime.strptime(fecha_str, "%d/%m/%Y")
            except:
                return datetime.min
        columnas_precios.sort(key=ordenar_fecha_precio)
        
        # Construir orden final
        orden_final = []
        for col in orden_basico:
            if col in df_sheets.columns:
                orden_final.append(col)
        orden_final.extend(columnas_precios)
        
        # Aplicar orden
        try:
            df_final = df_sheets[orden_final]
            
            # VERIFICACIÓN FINAL: Asegurar que no hay valores problemáticos
            for column in df_final.columns:
                if df_final[column].dtype in ['float64', 'int64']:
                    # Última verificación de valores problemáticos
                    has_inf = np.isinf(df_final[column]).any()
                    has_nan = df_final[column].isna().any()
                    if has_inf or has_nan:
                        print(f"ADVERTENCIA V1.4: Limpiando valores finales en {column}")
                        df_final[column] = df_final[column].replace([np.inf, -np.inf], 0)
                        df_final[column] = df_final[column].fillna(0)
            
            print(f"V1.4: Preparación completada - {len(df_final)} filas, {len(df_final.columns)} columnas")
            print(f"V1.4: Precios al final: {columnas_precios}")
            
            return df_final
            
        except Exception as e:
            print(f"ERROR V1.4 aplicando orden: {e}")
            return df_sheets
    
    def guardar_historico_actualizado(self, df_historico):
        """V1.4: Guarda el historico con verificaciones adicionales"""
        try:
            print("V1.4: Guardando historico con verificaciones...")
            
            # Preparar datos con limpieza exhaustiva
            df_sheets = self.preparar_dataframe_para_sheets(df_historico)
            
            # Verificación adicional antes de guardar
            print("V1.4: Verificación final antes de guardar...")
            total_nan = df_sheets.isna().sum().sum()
            total_inf = 0
            
            for col in df_sheets.columns:
                if df_sheets[col].dtype in ['float64', 'int64']:
                    total_inf += np.isinf(df_sheets[col]).sum()
            
            print(f"V1.4: Verificación - NaN: {total_nan}, Infinitos: {total_inf}")
            
            if total_nan > 0 or total_inf > 0:
                print("V1.4: Aplicando limpieza final de emergencia...")
                df_sheets = df_sheets.fillna('')
                for col in df_sheets.columns:
                    if df_sheets[col].dtype in ['float64', 'int64']:
                        df_sheets[col] = df_sheets[col].replace([np.inf, -np.inf], 0)
            
            # Abrir spreadsheet
            spreadsheet = self.gs_handler.client.open_by_key(self.sheet_id)
            
            # Crear o actualizar hoja Data_Historico
            try:
                worksheet_historico = spreadsheet.worksheet("Data_Historico")
                worksheet_historico.clear()
                print("V1.4: Hoja Data_Historico limpiada")
            except:
                worksheet_historico = spreadsheet.add_worksheet(
                    title="Data_Historico",
                    rows=len(df_sheets) + 10,
                    cols=len(df_sheets.columns) + 5
                )
                print("V1.4: Hoja Data_Historico creada")
            
            # Preparar datos para subir - CONVERSIÓN SEGURA
            headers = df_sheets.columns.values.tolist()
            
            # Convertir datos a formato seguro para Google Sheets
            data_rows = []
            for _, row in df_sheets.iterrows():
                safe_row = []
                for value in row:
                    if pd.isna(value):
                        safe_row.append('')
                    elif isinstance(value, (int, float)):
                        if np.isinf(value) or np.isnan(value):
                            safe_row.append(0)
                        else:
                            safe_row.append(value)
                    else:
                        safe_row.append(str(value))
                data_rows.append(safe_row)
            
            all_data = [headers] + data_rows
            
            # Subir datos
            worksheet_historico.update(all_data)
            
            print(f"V1.4: EXITO - Historico guardado con {len(df_sheets)} coches")
            columnas_precio = len([col for col in headers if col.startswith('Precio_')])
            print(f"V1.4: Columnas precio: {columnas_precio}")
            print(f"URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}")
            
            return True
            
        except Exception as e:
            print(f"ERROR V1.4 guardando historico: {str(e)}")
            return False
    
    def mostrar_resumen_final(self):
        """Muestra el resumen final"""
        tiempo_total = (datetime.now() - self.tiempo_inicio).total_seconds()
        self.stats['tiempo_ejecucion'] = tiempo_total
        
        print(f"\n{'='*80}")
        print("PROCESAMIENTO COMPLETADO - ANALISIS HISTORICO COCHES V1.4 ORDEN MARCA")
        print("="*80)
        print(f"Fecha procesada: {self.fecha_display}")
        print(f"Coches en scraper: {self.stats['total_archivo_nuevo']:,}")
        print(f"Coches en historico: {self.stats['total_historico']:,}")
        print(f"Coches nuevos detectados: {self.stats['coches_nuevos']:,}")
        print(f"Coches actualizados: {self.stats['coches_actualizados']:,}")
        print(f"Coches vendidos: {self.stats['coches_vendidos']:,}")
        print(f"Errores procesamiento: {self.stats['errores']:,}")
        print(f"Tiempo ejecucion: {tiempo_total:.2f} segundos")
        
        if self.cambios_precio:
            print(f"\nCAMBIOS DE PRECIO DETECTADOS: {len(self.cambios_precio)}")
            for cambio in self.cambios_precio[:3]:
                print(f"  {cambio['Marca']} {cambio['Modelo']} - {cambio['Vendedor']}")
                print(f"    {cambio['Precio_Anterior']} -> {cambio['Precio_Nuevo']}")
        
        print(f"\nNueva columna: Precio_{self.fecha_display}")
        print("CORRECCION V1.4 - ORDEN MARCA ALFABÉTICO:")
        print("    Regeneración de columnas internas al leer histórico")
        print("    Limpieza exhaustiva de valores problemáticos")
        print("    Manejo seguro de tipos de datos mixtos")
        print("    Fix completo para 'Out of range float values'")
        print("    NUEVO: Ordenamiento por Vendedor (A-Z) -> Marca alfabética (A-Z)")
        print("    Orden columnas: Básicos -> Características -> Control -> PRECIOS AL FINAL")
    
    def ejecutar(self):
        """Funcion principal que ejecuta todo el proceso"""
        try:
            # 1. Inicializar Google Sheets
            if not self.inicializar_google_sheets():
                return False
            
            # 2. Leer datos unificados del scraper
            df_nuevo = self.leer_datos_scraper_unificados()
            
            # 3. Mostrar header
            self.mostrar_header()
            
            # 4. Procesar segun si es primera vez o no
            df_historico_existente = self.leer_historico_existente()
            
            if df_historico_existente is None:
                # Primera ejecucion
                df_historico_final = self.primera_ejecucion(df_nuevo)
            else:
                # Actualizar historico existente
                df_historico_final = self.procesar_coches_nuevos_y_existentes(df_nuevo, df_historico_existente)
            
            self.stats['total_historico'] = len(df_historico_final)
            
            # 5. Guardar historico actualizado
            success = self.guardar_historico_actualizado(df_historico_final)
            
            if not success:
                print("ERROR: No se pudo guardar el historico")
                return False
            
            # 6. Mostrar resumen final
            self.mostrar_resumen_final()
            return True
            
        except Exception as e:
            print(f"\nERROR CRITICO V1.4: {str(e)}")
            print("El procesamiento no se pudo completar correctamente")
            
            import traceback
            traceback.print_exc()
            
            return False

def main():
    """Funcion principal del analizador"""
    print("Iniciando Analizador Historico COCHES V1.4 ORDEN MARCA ALFABÉTICO...")
    print("CORRECCION V1.4:")
    print("    FIX COMPLETO para 'Out of range float values are not JSON compliant'")
    print("    Regeneración de columnas internas al leer histórico existente")
    print("    Limpieza exhaustiva de valores problemáticos (NaN, inf, extremos)")
    print("    Manejo seguro de tipos de datos mixtos (histórico + scraper)")
    print("    Conversión segura a formato Google Sheets compatible")
    print("    Verificaciones adicionales antes de guardar")
    print("    PRECIOS AL FINAL del dataframe (orden corregido)")
    print("    NUEVO: Ordenamiento por Vendedor (A-Z) -> Marca alfabética (A-Z)")
    print()
    
    analizador = AnalizadorHistoricoCoches()
    exito = analizador.ejecutar()
    
    if exito:
        print("\nPROCESO COMPLETADO EXITOSAMENTE V1.4")
        print("CORRECCION V1.4 APLICADA:")
        print("    Error 'Out of range float values' SOLUCIONADO")
        print("    Histórico actualizado correctamente")
        print("    Precios acumulándose cronológicamente al final")
        print("    NUEVO: Ordenamiento por Vendedor -> Marca alfabética")
        
        return True
    else:
        print("\nProceso completado con errores")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
