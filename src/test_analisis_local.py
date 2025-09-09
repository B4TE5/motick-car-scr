"""
===============================================================================
                     CONFIG ANALISIS · WALLAPOP SCRAPER V1.1
===============================================================================

Descripción:
    Configuración específica para el módulo de análisis histórico de coches.
    MODIFICADO V1.1: Solo precio al contado, sin columnas auxiliares en Sheets.

CAMBIOS V1.1:
    - Solo precio al contado (renombrado a Precio_FECHA)
    - Sin precio financiado
    - Sin columnas numéricas auxiliares en Google Sheets
    - Precios guardados TODOS los días

Autor: Carlos Peraza
Versión: 1.1
Fecha: Septiembre 2025
Compatibilidad: Python 3.10+
Uso: Motick

===============================================================================
"""

import os
from datetime import datetime

# Configuración de Google Sheets para Análisis Histórico
SHEET_NAME_HISTORICO = "Data_Historico"
SHEET_NAME_PATTERN_J1 = "SCR-J1 {fecha}"
SHEET_NAME_PATTERN_J2 = "SCR-J2 {fecha}"

# Configuración de columnas para el histórico
COLUMNAS_PRECIO_BASE = ["Precio_Contado"]  # Solo contado
COLUMNAS_IDENTIFICACION = ["URL", "Marca", "Modelo", "Vendedor"]
COLUMNAS_DATOS_ADICIONALES = ["Ano", "KM", "Tipo", "Combustible", "Potencia"]

# Columnas internas (NO se guardan en Google Sheets)
COLUMNAS_INTERNAS = ["KM_Numerico_Internal", "Ano_Numerico_Internal"]

# Configuración de detección de cambios
PRECIO_CAMBIO_MINIMO = 100  # Euros - cambio mínimo para considerar significativo
PRECIO_MAXIMO_VALIDO = 500000  # Euros - precio máximo válido
PRECIO_MINIMO_VALIDO = 500   # Euros - precio mínimo válido

# Configuración de estados
ESTADOS_VALIDOS = ["activo", "vendido", "retirado"]
ESTADO_INICIAL = "activo"
ESTADO_VENDIDO = "vendido"

# Configuración de ordenamiento
ORDENAMIENTO_PRINCIPAL = ["Vendedor", "Estado"]
ORDENAMIENTO_SECUNDARIO = ["KM_Numerico_Internal"]  # Descendente (mayor a menor KM) - SOLO INTERNO
ORDENAMIENTO_VENDIDOS = ["Fecha_Venta"]

# Patrones de limpieza de precios
PATRONES_PRECIO_LIMPIEZA = [
    r'(\d+(?:\.\d{3})*)\s*€',  # Formato con puntos como separador de miles
    r'(\d+(?:,\d{3})*)\s*€',   # Formato con comas como separador de miles  
    r'(\d+)\s*€',              # Formato simple
    r'(\d+(?:\.\d{3})*)\s*euros?',  # Con palabra "euro"
    r'(\d+(?:,\d{3})*)\s*euros?'
]

# Patrones de limpieza de kilometraje
PATRONES_KM_LIMPIEZA = [
    r'(\d+(?:\.\d{3})*)\s*km',
    r'(\d+(?:,\d{3})*)\s*km', 
    r'(\d+)\s*km',
    r'(\d+(?:\.\d{3})*)\s*kilómetros?',
    r'(\d+(?:,\d{3})*)\s*kilómetros?'
]

# Configuración de análisis de tendencias
DIAS_PARA_TENDENCIA = 7  # Mínimo de días para calcular tendencias
CAMBIO_PORCENTAJE_SIGNIFICATIVO = 5  # Porcentaje mínimo para considerar cambio significativo

# Configuración de logging y reportes
MOSTRAR_DETALLES_CAMBIOS_PRECIO = True
MOSTRAR_TOP_VARIACIONES = 5
MOSTRAR_COCHES_NUEVOS_DETALLE = True
MOSTRAR_VENDIDOS_DETALLE = True

# Configuración de validación de datos
VALIDACIONES = {
    'url_requerida': True,
    'precio_contado_requerido': False,  # Puede ser "No especificado"
    'marca_requerida': True,
    'modelo_requerido': True,
    'vendedor_requerido': True
}

# Configuración de backup y recuperación
CREAR_BACKUP_ANTES_ACTUALIZACION = True
DIAS_RETENCION_BACKUP = 30

def get_fecha_actual_formateada():
    """Obtiene la fecha actual en formato DD/MM/YYYY"""
    return datetime.now().strftime("%d/%m/%Y")

def get_nombres_hojas_scraper(fecha_str=None):
    """Obtiene los nombres de las hojas del scraper para una fecha específica"""
    if fecha_str is None:
        fecha_str = get_fecha_actual_formateada()
    
    return {
        'job1': SHEET_NAME_PATTERN_J1.format(fecha=fecha_str),
        'job2': SHEET_NAME_PATTERN_J2.format(fecha=fecha_str)
    }

def get_columna_precio_fecha(fecha_str):
    """Obtiene el nombre de la columna de precio para una fecha específica"""
    # MODIFICADO V1.1: Solo una columna de precio (sin "Contado")
    return f"Precio_{fecha_str}"

def validar_precio(precio_str):
    """Valida si un precio está dentro de rangos esperados"""
    if not precio_str or precio_str == "No especificado":
        return True, 0
    
    # Limpiar y extraer número del precio
    for patron in PATRONES_PRECIO_LIMPIEZA:
        import re
        match = re.search(patron, str(precio_str), re.IGNORECASE)
        if match:
            try:
                precio_num = int(match.group(1).replace('.', '').replace(',', ''))
                if PRECIO_MINIMO_VALIDO <= precio_num <= PRECIO_MAXIMO_VALIDO:
                    return True, precio_num
                else:
                    return False, precio_num
            except:
                continue
    
    return False, 0

def limpiar_kilometraje(km_str):
    """Limpia y extrae el valor numérico del kilometraje"""
    if not km_str or km_str == "No especificado":
        return 0
    
    # Limpiar y extraer número del kilometraje
    for patron in PATRONES_KM_LIMPIEZA:
        import re
        match = re.search(patron, str(km_str), re.IGNORECASE)
        if match:
            try:
                km_num = int(match.group(1).replace('.', '').replace(',', ''))
                return km_num
            except:
                continue
    
    # Fallback: extraer cualquier número
    import re
    numeros = re.findall(r'\d+', str(km_str).replace('.', '').replace(',', ''))
    if numeros:
        try:
            return int(''.join(numeros))
        except:
            pass
    
    return 0

def limpiar_ano(ano_str):
    """Limpia y extrae el valor numérico del año"""
    if not ano_str or ano_str == "No especificado":
        return 0
    
    import re
    numeros = re.findall(r'\d{4}', str(ano_str))
    if numeros:
        ano = int(numeros[0])
        if 1990 <= ano <= datetime.now().year + 1:
            return ano
    return 0

def es_cambio_precio_significativo(precio_anterior, precio_nuevo):
    """Determina si un cambio de precio es significativo"""
    try:
        if not precio_anterior or not precio_nuevo:
            return False
        
        # Si ambos son strings con "No especificado", no es cambio
        if str(precio_anterior) == "No especificado" and str(precio_nuevo) == "No especificado":
            return False
        
        # Si uno cambia de/a "No especificado", es significativo
        if str(precio_anterior) == "No especificado" or str(precio_nuevo) == "No especificado":
            return True
        
        # Extraer valores numéricos
        _, valor_anterior = validar_precio(precio_anterior)
        _, valor_nuevo = validar_precio(precio_nuevo)
        
        if valor_anterior == 0 or valor_nuevo == 0:
            return False
        
        # Calcular diferencia absoluta
        diferencia = abs(valor_nuevo - valor_anterior)
        
        # Es significativo si supera el mínimo O el porcentaje
        return (diferencia >= PRECIO_CAMBIO_MINIMO or 
                (diferencia / valor_anterior * 100) >= CAMBIO_PORCENTAJE_SIGNIFICATIVO)
        
    except:
        return False

def get_configuracion_ordenamiento():
    """Obtiene la configuración de ordenamiento para el DataFrame final"""
    return {
        'activos': {
            'columnas': ORDENAMIENTO_PRINCIPAL + ORDENAMIENTO_SECUNDARIO,
            'ascendente': [True, True, False]  # Vendedor ASC, Estado ASC, KM DESC
        },
        'vendidos': {
            'columnas': ORDENAMIENTO_VENDIDOS,
            'ascendente': [False]  # Fecha_Venta DESC (más recientes primero)
        }
    }

def get_columnas_sheets_finales():
    """Define qué columnas deben aparecer en Google Sheets (excluyendo internas)"""
    columnas_base = [
        'ID_Unico_Coche',
        'Marca', 
        'Modelo',
        'Vendedor',
        'Ano',
        'KM',
        'URL',
        'Primera_Deteccion',
        'Estado',
        'Fecha_Venta'
    ]
    
    # Las columnas de precio se añaden dinámicamente
    # Las columnas internas NO se incluyen
    
    return columnas_base

def get_columnas_excluir_sheets():
    """Define qué columnas NO deben aparecer en Google Sheets"""
    return COLUMNAS_INTERNAS + [
        'Precio_Contado',      # Se renombra a Precio_FECHA
        'Precio_Financiado'    # No se incluye en V1.1
    ]

# Configuración de mensajes y logging - MODIFICADO V1.1
MENSAJES = {
    'inicio_analisis': "Iniciando análisis histórico de coches V1.1...",
    'datos_unificados': "Datos de scraper unificados exitosamente",
    'historico_leido': "Histórico existente leído correctamente", 
    'primera_ejecucion': "Primera ejecución - creando histórico inicial",
    'actualizacion_completada': "Actualización de histórico completada",
    'error_critico': "Error crítico en el análisis",
    'guardado_exitoso': "Histórico guardado exitosamente en Google Sheets",
    'proceso_completado': "Proceso de análisis histórico completado V1.1",
    'cambios_v11': "MODIFICACIONES V1.1: Solo precio contado, sin columnas auxiliares"
}

# Configuración para testing local
TESTING_CONFIG = {
    'usar_datos_mock': False,
    'limite_coches_testing': 100,
    'simular_cambios_precio': False,
    'mostrar_debug_detallado': True,
    'solo_precio_contado': True,  # NUEVO V1.1
    'excluir_columnas_internas': True  # NUEVO V1.1
}

def get_config_testing():
    """Obtiene configuración para testing local"""
    return TESTING_CONFIG if os.getenv('TEST_MODE', 'false').lower() == 'true' else None

def validar_estructura_historico_v11(df):
    """Valida que el historico tenga la estructura correcta V1.1"""
    print("Validando estructura V1.1...")
    
    # Verificar que NO tiene columnas que no debería tener
    columnas_prohibidas = get_columnas_excluir_sheets()
    columnas_encontradas_prohibidas = [col for col in columnas_prohibidas if col in df.columns]
    
    if columnas_encontradas_prohibidas:
        print(f"ADVERTENCIA: Encontradas columnas que deberían estar excluidas: {columnas_encontradas_prohibidas}")
    
    # Verificar que tiene columnas de precio en formato correcto
    columnas_precio = [col for col in df.columns if col.startswith('Precio_')]
    columnas_precio_incorrectas = [col for col in columnas_precio if 'Contado' in col or 'Financiado' in col]
    
    if columnas_precio_incorrectas:
        print(f"ADVERTENCIA: Encontradas columnas precio en formato incorrecto: {columnas_precio_incorrectas}")
        print("Formato esperado: Precio_DD/MM/YYYY")
    
    print(f"Columnas precio correctas: {len(columnas_precio) - len(columnas_precio_incorrectas)}")
    print(f"Estructura V1.1 validada")
    
    return True

def debug_mostrar_estructura_final(df, titulo="ESTRUCTURA FINAL"):
    """Función de debug para mostrar la estructura del DataFrame"""
    print(f"\n{'-'*50}")
    print(f"{titulo}")
    print(f"{'-'*50}")
    print(f"Total filas: {len(df)}")
    print(f"Total columnas: {len(df.columns)}")
    
    columnas_precio = [col for col in df.columns if col.startswith('Precio_')]
    columnas_internas = [col for col in df.columns if col.endswith('_Internal')]
    
    print(f"Columnas precio: {len(columnas_precio)}")
    if columnas_precio:
        print(f"  {columnas_precio}")
    
    print(f"Columnas internas: {len(columnas_internas)}")
    if columnas_internas:
        print(f"  {columnas_internas}")
    
    print(f"Estados: {df['Estado'].value_counts().to_dict() if 'Estado' in df.columns else 'N/A'}")
    print(f"{'-'*50}\n")
