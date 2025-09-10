"""
Analizador Historico Coches - Version Google Sheets V1.1 CORREGIDO
Lee datos del scraper desde Google Sheets y actualiza el historico evolutivo de precios

CORRECCION CRITICA:
- Formato fecha corregido: SCR-J1 DD/MM/YY (año corto)
- Mapeo columnas corregido para datos reales del scraper
- Validaciones ajustadas para estructura real
- Manejo errores mejorado
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
        print("ANALIZADOR HISTORICO COCHES V1.1 - VERSION CORREGIDA")
        print("="*80)
        print(f"Fecha procesamiento: {self.fecha_display}")
        print("Logica: URL como identificador unico principal")
        print("Fuente: Google Sheets (Une SCR-J1 y SCR-J2)")
        print("Destino: Hoja Data_Historico")
        print("Precio: SOLO precio al contado (columnas Precio_FECHA)")
        print("Ordenacion: Vendedor -> Kilometraje (mayor a menor)")
        print()
    
    def leer_datos_scraper_unificados(self):
        """Lee y unifica datos de ambos jobs del scraper - CORREGIDO"""
        try:
            print("Leyendo datos de jobs del scraper...")
            
            # CORRECCION CRITICA: Usar formato de fecha correcto
            fecha_hoy = datetime.now()
            fecha_str_corta = fecha_hoy.strftime("%d/%m/%y")  # FORMATO CORTO: 10/09/25
            
            # Nombres de las hojas que buscaremos (FORMATO REAL DEL SCRAPER)
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
        """Valida que el archivo tenga la estructura esperada - CORREGIDO"""
        print(f"Validando estructura de datos...")
        
        # MAPEO CORREGIDO: Columnas reales del scraper
        mapeo_columnas = {
            'Precio al Contado': 'Precio_Contado',
            'Precio Financiado': 'Precio_Financiado', 
            'Fecha Extraccion': 'Fecha_Extraccion',
            'AÃ±o': 'Ano',
            'Año': 'Ano',
            'Aï¿½o': 'Ano',  # Codificacion rara
            'Aï¿½ï¿½o': 'Ano',  # Codificacion rara
            'NÂº Plazas': 'Plazas',
            'NÂº Puertas': 'Puertas',
            'ConducciÃ³n': 'Conduccion',
            'ConducciÃÂ³n': 'Conduccion',
            'Potencia': 'Potencia'
        }
        
        df = df.rename(columns=mapeo_columnas)
        
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
        """Lee el historico existente desde Google Sheets"""
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
                
                # Crear columnas numericas internas si no existen (para ordenamiento)
                if 'KM_Numerico_Internal' not in df_historico.columns:
                    df_historico['KM_Numerico_Internal'] = df_historico.get('KM', 'No especificado').apply(self.limpiar_km_interno)
                
                if 'Ano_Numerico_Internal' not in df_historico.columns:
                    df_historico['Ano_Numerico_Internal'] = df_historico.get('Ano', 'No especificado').apply(self.limpiar_ano_interno)
                
                self.stats['total_historico'] = len(df_historico)
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
    
    def limpiar_km_interno(self, km_text):
        """Funcion auxiliar para limpiar KM"""
        if pd.isna(km_text) or km_text == 'No especificado':
            return 0
        numeros = re.findall(r'\d+', str(km_text).replace('.', '').replace(',', ''))
        if numeros:
            return int(''.join(numeros))
        return 0
    
    def limpiar_ano_interno(self, ano_text):
        """Funcion auxiliar para limpiar año"""
        if pd.isna(ano_text) or ano_text == 'No especificado':
            return 0
        numeros = re.findall(r'\d{4}', str(ano_text))
        if numeros:
            ano = int(numeros[0])
            if 1990 <= ano <= datetime.now().year + 1:
                return ano
        return 0
    
    def primera_ejecucion(self, df_nuevo):
        """Crea el historico por primera vez"""
        print("Primera ejecucion - Creando historico inicial")
        
        df_historico = df_nuevo.copy()
        
        # Columnas de control
        df_historico['Primera_Deteccion'] = self.fecha_display
        df_historico['Estado'] = 'activo'
        df_historico['Fecha_Venta'] = pd.NA
        
        # Columna de precio para la fecha actual (SOLO CONTADO, renombrado a Precio_)
        col_precio_hoy = f"Precio_{self.fecha_display}"
        df_historico[col_precio_hoy] = df_historico['Precio_Contado']
        
        # Eliminar columnas que no queremos en Google Sheets
        columnas_a_eliminar = [
            'Precio_Contado', 
            'Precio_Financiado',  # No la queremos
            'KM_Numerico_Internal',  # Solo para uso interno
            'Ano_Numerico_Internal'  # Solo para uso interno
        ]
        
        columnas_existentes_a_eliminar = [col for col in columnas_a_eliminar if col in df_historico.columns]
        if columnas_existentes_a_eliminar:
            df_historico = df_historico.drop(columnas_existentes_a_eliminar, axis=1)
        
        # Reordenar columnas
        columnas_base = ['ID_Unico_Coche', 'Marca', 'Modelo', 'Vendedor', 'Ano', 'KM', 'URL', 'Primera_Deteccion', 'Estado', 'Fecha_Venta']
        columnas_precio = [col_precio_hoy]
        
        columnas_finales = []
        for col in columnas_base:
            if col in df_historico.columns:
                columnas_finales.append(col)
        
        columnas_finales.extend(columnas_precio)
        
        # Añadir columnas extra que puedan existir
        for col in df_historico.columns:
            if col not in columnas_finales:
                columnas_finales.append(col)
        
        df_historico = df_historico[columnas_finales]
        
        # Ordenar por vendedor y kilometraje
        df_historico = self.ordenar_dataframe(df_historico)
        
        self.stats['total_historico'] = len(df_historico)
        self.stats['coches_nuevos'] = len(df_historico)
        self.coches_nuevos_lista = df_historico[['Marca', 'Modelo', 'Vendedor']].to_dict('records')
        
        return df_historico
    
    def procesar_coches_nuevos_y_existentes(self, df_nuevo, df_historico):
        """Procesa coches nuevos y actualiza existentes"""
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
            df_actualizado[col_precio_hoy] = pd.NA
            
            # PROCESAR COCHES EXISTENTES
            for url_coche in coches_existentes_urls:
                try:
                    fila_nueva = df_nuevo[df_nuevo['URL'] == url_coche].iloc[0]
                    precio_nuevo = fila_nueva['Precio_Contado']
                    
                    mask = df_actualizado['URL'] == url_coche
                    df_actualizado.loc[mask, col_precio_hoy] = precio_nuevo
                    df_actualizado.loc[mask, 'Estado'] = 'activo'
                    
                    # Detectar cambios de precio
                    if fecha_anterior:
                        col_precio_anterior = f"Precio_{fecha_anterior}"
                        if col_precio_anterior in df_actualizado.columns:
                            precio_anterior = df_actualizado.loc[mask, col_precio_anterior].iloc[0]
                            if pd.notna(precio_anterior) and precio_anterior != precio_nuevo:
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
                        'Fecha_Venta': pd.NA
                    }
                    
                    # Inicializar todas las columnas de precios anteriores con NA
                    for col_precio in columnas_precios:
                        nueva_fila[col_precio] = pd.NA
                    
                    # Anadir precio para la fecha actual
                    nueva_fila[col_precio_hoy] = fila_nueva['Precio_Contado']
                    
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
            
            # Regenerar columnas internas para ordenamiento de coches existentes
            if 'KM_Numerico_Internal' not in df_actualizado.columns:
                df_actualizado['KM_Numerico_Internal'] = df_actualizado['KM'].apply(self.limpiar_km_interno)
            if 'Ano_Numerico_Internal' not in df_actualizado.columns:
                df_actualizado['Ano_Numerico_Internal'] = df_actualizado['Ano'].apply(self.limpiar_ano_interno)
            
            # Ordenar resultado final
            df_actualizado = self.ordenar_dataframe(df_actualizado)
            
            return df_actualizado
            
        except Exception as e:
            print(f"ERROR critico en procesamiento: {str(e)}")
            raise
    
    def reordenar_columnas_consistente(self, df):
        """Reordena las columnas en el orden específico solicitado"""
        try:
            # ORDEN ESPECIFICO: Datos del coche -> URL y control -> Precios por fecha
            columnas_datos_coche = ['ID_Unico_Coche', 'Marca', 'Modelo', 'Vendedor', 'Ano', 'KM', 'Tipo', 'Plazas', 'Puertas', 'Combustible', 'Potencia', 'Conduccion']
            columnas_url_control = ['URL', 'Primera_Deteccion', 'Estado', 'Fecha_Venta']
            
            # Obtener columnas de precios (ordenadas por fecha)
            columnas_precios = [col for col in df.columns if col.startswith('Precio_')]
            columnas_precios.sort()  # Ordenar cronológicamente
            
            # Construir orden final
            columnas_ordenadas = []
            
            # 1. Añadir columnas de datos del coche
            for col in columnas_datos_coche:
                if col in df.columns:
                    columnas_ordenadas.append(col)
            
            # 2. Añadir columnas de URL y control
            for col in columnas_url_control:
                if col in df.columns:
                    columnas_ordenadas.append(col)
            
            # 3. Añadir columnas de precios al final
            columnas_ordenadas.extend(columnas_precios)
            
            # 4. Añadir cualquier columna extra que no esté en las listas
            for col in df.columns:
                if col not in columnas_ordenadas and not col.endswith('_Internal'):  # Excluir internas
                    columnas_ordenadas.append(col)
            
            # Reordenar DataFrame
            columnas_existentes = [col for col in columnas_ordenadas if col in df.columns]
            return df[columnas_existentes]
            
        except Exception as e:
            print(f"ADVERTENCIA: Error reordenando columnas: {str(e)}")
            return df

    def ordenar_dataframe(self, df):
        """Ordena el dataframe por Vendedor y luego por Kilometraje (mayor a menor)"""
        try:
            print("Ordenando datos por Vendedor y Kilometraje...")
            
            # Separar coches activos y vendidos
            df_activos = df[df['Estado'] == 'activo'].copy()
            df_vendidos = df[df['Estado'] == 'vendido'].copy()
            
            # Ordenar activos por Vendedor y luego por KM_Numerico_Internal (mayor a menor)
            if not df_activos.empty:
                df_activos = df_activos.sort_values(
                    ['Vendedor', 'KM_Numerico_Internal'], 
                    ascending=[True, False],  # Vendedor A-Z, KM mayor a menor
                    na_position='last'
                )
            
            # Ordenar vendidos por fecha de venta
            if not df_vendidos.empty and 'Fecha_Venta' in df_vendidos.columns:
                df_vendidos = df_vendidos.sort_values(
                    'Fecha_Venta', 
                    ascending=False,
                    na_position='last'
                )
            
            # Concatenar: activos arriba, vendidos abajo
            df_ordenado = pd.concat([df_activos, df_vendidos], ignore_index=True)
            
            return df_ordenado
            
        except Exception as e:
            print(f"ADVERTENCIA: Error ordenando datos: {str(e)}")
            return df
    
    def preparar_dataframe_para_sheets(self, df_historico):
        """Prepara el dataframe eliminando columnas internas antes de guardar en Google Sheets"""
        print("Preparando datos para Google Sheets...")
        
        df_sheets = df_historico.copy()
        
        # ELIMINAR COLUMNAS INTERNAS (no queremos que aparezcan en Google Sheets)
        columnas_internas = [
            'KM_Numerico_Internal',
            'Ano_Numerico_Internal'
        ]
        
        columnas_a_eliminar = [col for col in columnas_internas if col in df_sheets.columns]
        if columnas_a_eliminar:
            df_sheets = df_sheets.drop(columnas_a_eliminar, axis=1)
            print(f"Columnas internas eliminadas: {columnas_a_eliminar}")
        
        return df_sheets
    
    def guardar_historico_actualizado(self, df_historico):
        """Guarda el historico actualizado en Google Sheets"""
        try:
            print("Guardando historico actualizado en Google Sheets...")
            
            # Preparar datos (eliminar columnas internas)
            df_sheets = self.preparar_dataframe_para_sheets(df_historico)
            
            # Abrir spreadsheet
            spreadsheet = self.gs_handler.client.open_by_key(self.sheet_id)
            
            # Crear o actualizar hoja Data_Historico
            try:
                worksheet_historico = spreadsheet.worksheet("Data_Historico")
                worksheet_historico.clear()
                print("Hoja Data_Historico limpiada")
            except:
                worksheet_historico = spreadsheet.add_worksheet(
                    title="Data_Historico",
                    rows=len(df_sheets) + 10,
                    cols=len(df_sheets.columns) + 5
                )
                print("Hoja Data_Historico creada")
            
            # Preparar datos para subir
            headers = df_sheets.columns.values.tolist()
            data_rows = df_sheets.fillna('').values.tolist()  # Reemplazar NA con string vacio
            all_data = [headers] + data_rows
            
            # Subir datos
            worksheet_historico.update(all_data)
            
            print(f"EXITO: Historico guardado con {len(df_sheets)} coches")
            print(f"Columnas precio: {len([col for col in headers if col.startswith('Precio_')])}")
            print(f"URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}")
            
            return True
            
        except Exception as e:
            print(f"ERROR guardando historico: {str(e)}")
            return False
    
    def mostrar_resumen_final(self):
        """Muestra el resumen final"""
        tiempo_total = (datetime.now() - self.tiempo_inicio).total_seconds()
        self.stats['tiempo_ejecucion'] = tiempo_total
        
        print(f"\n{'='*80}")
        print("PROCESAMIENTO COMPLETADO - ANALISIS HISTORICO COCHES V1.1 CORREGIDO")
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
            for cambio in self.cambios_precio[:3]:  # Mostrar solo los primeros 3
                print(f"  {cambio['Marca']} {cambio['Modelo']} - {cambio['Vendedor']}")
                print(f"    {cambio['Precio_Anterior']} -> {cambio['Precio_Nuevo']}")
        
        if self.stats['errores'] > 0:
            print(f"\nADVERTENCIAS:")
            print(f"Se produjeron {self.stats['errores']} errores durante el procesamiento")
        
        print(f"\nNueva columna: Precio_{self.fecha_display}")
        print("CORRECCION V1.1:")
        print("  - Formato fecha corregido (DD/MM/YY)")
        print("  - Mapeo columnas ajustado al scraper real")
        print("  - SOLO precio al contado (columnas Precio_FECHA)")
        print("  - SIN columnas numericas auxiliares en Google Sheets")
        print("  - SIN precio financiado")
        print("  - Precios guardados TODOS los dias de extraccion")
        print("  - Ordenacion: Vendedor -> Kilometraje (mayor a menor)")
    
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
            print(f"\nERROR CRITICO: {str(e)}")
            print("El procesamiento no se pudo completar correctamente")
            
            import traceback
            traceback.print_exc()
            
            return False

def main():
    """Funcion principal del analizador"""
    print("Iniciando Analizador Historico COCHES V1.1 CORREGIDO...")
    print("CORRECION CRITICA:")
    print("   - Formato fecha corregido: SCR-J1 DD/MM/YY (año corto)")
    print("   - Lee datos del scraper desde Google Sheets (SCR-J1 y SCR-J2)")
    print("   - Unifica ambos jobs en un solo dataset")
    print("   - SOLO rastrea precio al contado (columnas Precio_FECHA)")
    print("   - NO incluye precio financiado")
    print("   - NO guarda columnas numericas auxiliares en Google Sheets")
    print("   - USA URL como identificador unico")
    print("   - Detecta ventas cuando coches desaparecen")
    print("   - Ordena por Vendedor y Kilometraje (mayor a menor)")
    print("   - Guarda precios TODOS los dias (suban o bajen)")
    print()
    
    analizador = AnalizadorHistoricoCoches()
    exito = analizador.ejecutar()
    
    if exito:
        print("\nPROCESO COMPLETADO EXITOSAMENTE V1.1 CORREGIDO")
        print("FORMATO DEL HISTORICO MODIFICADO:")
        print("   - Columnas basicas: Marca, Modelo, Vendedor, Ano, KM, URL, etc.")
        print("   - Columnas de control: Primera_Deteccion, Estado, Fecha_Venta")
        print("   - Columnas por fecha: Precio_DD/MM/YYYY (SOLO CONTADO)")
        print("   - SIN columnas numericas auxiliares en Google Sheets")
        print("   - ORDENACION: Activos arriba (Vendedor->KM desc), vendidos abajo")
        print("   - IDENTIFICACION: URL como clave unica principal")
        print("   - FORMATO FECHA CORREGIDO: DD/MM/YY (coincide con scraper)")
        
        return True
    else:
        print("\nProceso completado con errores")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
