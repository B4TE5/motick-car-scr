"""
Google Sheets Uploader para Wallapop Scraper
Sube datos de coches a Google Sheets de forma automatica
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os
from datetime import datetime

class GoogleSheetsUploader:
    def __init__(self, credentials_json_string=None, sheet_id=None, credentials_file=None):
        """
        Inicializar uploader con credenciales
        
        Args:
            credentials_json_string: String JSON de credenciales (para GitHub Actions)
            sheet_id: ID del Google Sheet
            credentials_file: Ruta al archivo de credenciales (para testing local)
        """
        if credentials_json_string:
            # Para GitHub Actions - desde string JSON
            credentials_dict = json.loads(credentials_json_string)
            self.credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
        elif credentials_file and os.path.exists(credentials_file):
            # Para testing local - desde archivo
            self.credentials = Credentials.from_service_account_file(
                credentials_file,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
        else:
            raise Exception("Se necesitan credenciales validas (JSON string o archivo)")
        
        self.client = gspread.authorize(self.credentials)
        self.sheet_id = sheet_id
        
        print("CONEXION: Google Sheets establecida correctamente")
        
    def test_connection(self):
        """Probar conexion a Google Sheets"""
        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            print(f"CONEXION: Exitosa al Sheet: {spreadsheet.title}")
            print(f"URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}")
            return True
        except Exception as e:
            print(f"ERROR CONEXION: {str(e)}")
            return False
    
    def upload_dataframe(self, df, worksheet_name="Datos_Actualizados"):
        """Subir DataFrame a una hoja especifica"""
        try:
            # Abrir Google Sheet
            spreadsheet = self.client.open_by_key(self.sheet_id)
            print(f"ACCEDIENDO: Sheet {spreadsheet.title}")
            
            # Crear o limpiar worksheet
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                worksheet.clear()
                print(f"LIMPIANDO: Hoja {worksheet_name}")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=len(df) + 10, 
                    cols=len(df.columns) + 2
                )
                print(f"CREANDO: Nueva hoja {worksheet_name}")
            
            # Preparar datos para subir
            headers = df.columns.values.tolist()
            data_rows = df.values.tolist()
            all_data = [headers] + data_rows
            
            # Subir datos
            worksheet.update(all_data)
            
            print(f"SUBIDA EXITOSA: {worksheet_name}")
            print(f"DATOS: {len(df)} filas x {len(df.columns)} columnas")
            
            return True
            
        except Exception as e:
            print(f"ERROR SUBIDA: {str(e)}")
            return False
    
    def upload_by_seller(self, df):
        """Crear hoja por fecha y job para ejecución paralela"""
        try:
            # Nombre de hoja basado en fecha actual Y VENDOR_GROUP
            today = datetime.now()
            vendor_group = os.getenv('VENDOR_GROUP', 'manual')
            
            # Crear nombre único para cada job
            if vendor_group == 'job1':
                sheet_name = f"SCR-J1 {today.strftime('%d/%m/%y')}"
            elif vendor_group == 'job2':
                sheet_name = f"SCR-J2 {today.strftime('%d/%m/%y')}"
            else:
                sheet_name = f"SCR {today.strftime('%d/%m/%y')}"
            
            print(f"\nSUBIENDO: Hoja {sheet_name}")
            
            spreadsheet = self.client.open_by_key(self.sheet_id)
            
            # Verificar si ya existe una hoja con este nombre
            try:
                existing_sheet = spreadsheet.worksheet(sheet_name)
                print(f"AVISO: Ya existe hoja {sheet_name} - sobrescribiendo")
                existing_sheet.clear()
                worksheet = existing_sheet
            except gspread.WorksheetNotFound:
                # Crear nueva hoja
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=len(df) + 10,
                    cols=len(df.columns) + 2
                )
                print(f"CREANDO: Nueva hoja {sheet_name}")
            
            # Subir datos
            headers = df.columns.values.tolist()
            data_rows = df.values.tolist()
            all_data = [headers] + data_rows
            
            worksheet.update(all_data)
            
            print(f"EXITO: {len(df)} coches subidos a {sheet_name}")
            print(f"URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}")
            
            return True
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return False
    
    def update_metadata(self, spreadsheet, df):
        """Crear hoja con estadisticas y metadata"""
        try:
            # Crear hoja de estadisticas
            try:
                meta_sheet = spreadsheet.worksheet("Estadisticas")
                meta_sheet.clear()
            except gspread.WorksheetNotFound:
                meta_sheet = spreadsheet.add_worksheet("Estadisticas", rows=20, cols=4)
            
            # Calcular estadisticas
            total_coches = len(df)
            vendedores_unicos = df['Vendedor'].nunique()
            marcas_unicas = df['Marca'].nunique()
            precios_contado_validos = len([p for p in df['Precio al Contado'] if p != 'No especificado'])
            precios_financiado_validos = len([p for p in df['Precio Financiado'] if p != 'No especificado'])
            
            # Estadisticas por vendedor
            stats_por_vendedor = []
            for vendedor in df['Vendedor'].unique():
                vendedor_df = df[df['Vendedor'] == vendedor]
                precios_contado_vendedor = len([p for p in vendedor_df['Precio al Contado'] if p != 'No especificado'])
                stats_por_vendedor.append([
                    vendedor,
                    len(vendedor_df),
                    vendedor_df['Marca'].nunique(),
                    f"{precios_contado_vendedor/len(vendedor_df)*100:.1f}%"
                ])
            
            # Preparar datos para la hoja
            metadata = [
                ["RESUMEN GENERAL", "", "", ""],
                ["Ultima Actualizacion", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "", ""],
                ["Total Coches", total_coches, "", ""],
                ["Vendedores Unicos", vendedores_unicos, "", ""],
                ["Marcas Unicas", marcas_unicas, "", ""],
                ["Precios Contado Extraidos", f"{precios_contado_validos}/{total_coches} ({precios_contado_validos/total_coches*100:.1f}%)", "", ""],
                ["Precios Financiado Extraidos", f"{precios_financiado_validos}/{total_coches} ({precios_financiado_validos/total_coches*100:.1f}%)", "", ""],
                ["Estado", "Completado", "", ""],
                ["Fuente", "Wallapop Scraper Automation", "", ""],
                ["", "", "", ""],
                ["ESTADISTICAS POR VENDEDOR", "", "", ""],
                ["Vendedor", "Total Coches", "Marcas Diferentes", "% Precios Extraidos"],
            ]
            
            # Agregar estadisticas por vendedor
            metadata.extend(stats_por_vendedor)
            
            # Subir metadata
            meta_sheet.update(metadata)
            
            print("ESTADISTICAS: Hoja creada exitosamente")
            return True
            
        except Exception as e:
            print(f"ERROR ESTADISTICAS: {e}")
            return False

def test_google_sheets_connection(sheet_id=None):
    """Funcion de prueba para verificar conexion"""
    print("PROBANDO CONEXION A GOOGLE SHEETS")
    print("=" * 50)
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv("../.env")  # Cargar desde raiz del proyecto
    
    if not sheet_id:
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        print(f"SHEET_ID desde .env: {sheet_id}")
    
    if not sheet_id:
        sheet_id = input("Introduce el Sheet ID manualmente: ")
    
    try:
        # Intentar cargar credenciales locales
        credentials_file = "../credentials/service-account.json"
        if not os.path.exists(credentials_file):
            print(f"ERROR: No se encontro el archivo de credenciales: {credentials_file}")
            return False
        
        # Crear uploader
        uploader = GoogleSheetsUploader(
            credentials_file=credentials_file,
            sheet_id=sheet_id
        )
        
        # Probar conexion
        if uploader.test_connection():
            print("\nCONEXION EXITOSA")
            
            # Crear datos de prueba
            test_data = {
                "Marca": ["Toyota", "BMW", "Audi"],
                "Modelo": ["Corolla", "X3", "A4"],
                "Vendedor": ["DURSAN D.", "DURSAN D.", "OCASIONPLUS E."],
                "Precio al Contado": ["15.000 euros", "25.000 euros", "20.000 euros"],
                "Fecha Extraccion": [datetime.now().strftime("%d/%m/%Y")] * 3
            }
            
            df_test = pd.DataFrame(test_data)
            print(f"\nSUBIENDO: Datos de prueba...")
            
            if uploader.upload_dataframe(df_test, "Prueba_Conexion"):
                print("EXITO: Datos de prueba subidos correctamente")
                print(f"REVISAR: https://docs.google.com/spreadsheets/d/{sheet_id}")
                return True
            else:
                print("ERROR: Subiendo datos de prueba")
                return False
        else:
            return False
            
    except Exception as e:
        print(f"ERROR EN PRUEBA: {str(e)}")
        return False

if __name__ == "__main__":
    # Ejecutar prueba si se ejecuta directamente
    test_google_sheets_connection()
