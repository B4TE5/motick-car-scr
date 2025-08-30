<div align="center">

# Wallapop Car Scraper

**Sistema automatizado de extracción de datos para concesionarios profesionales en Wallapop**

[![Build](https://img.shields.io/badge/Build-Passing-success)](https://github.com/your-repo/wallapop-scraper) [![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org) [![License](https://img.shields.io/badge/License-Private-red)](LICENSE)

## 📊 Dashboard de Datos en Vivo

**Ver datos extraídos:** [Google Sheets Dashboard](https://docs.google.com/spreadsheets/d/1drZonCFIP5BFuhbUW9cUauDQOWIVpE0V7P2ErpJq6bM/edit?gid=265284675#gid=265284675)

</div>

---

## Descripción General

Este sistema monitorea más de 18 concesionarios profesionales en Wallapop, extrayendo y organizando datos de inventario vehicular de forma automática. Diseñado para escalabilidad y confiabilidad sin intervención manual.

**Métricas Clave:**
- **5,000+** vehículos procesados diariamente
- **95%+** tasa de completitud de datos
- **3 horas** ventana de ejecución
- **Diario** ejecuciones automáticas a las 08:00 UTC

## Arquitectura

```
GitHub Actions → Motor Python → Selenium WebDriver → Procesamiento de Datos → Google Sheets
```

**Componentes Principales:**
- **Python 3.11** motor de procesamiento
- **Selenium WebDriver** con Chrome headless
- **Google Sheets API** para almacenamiento de datos
- **GitHub Actions** para automatización
- **Backups Excel** con retención de 30 días

## Inicio Rápido

### Requisitos Previos

- Repositorio GitHub con Actions habilitado
- Proyecto Google Cloud con API de Sheets habilitada
- Cuenta de servicio con permisos apropiados
- Google Sheet con permisos de compartición

### Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/your-repo/wallapop-scraper.git
   cd wallapop-scraper
   ```

2. **Configurar GitHub Secrets**
   
   Ir a `Settings → Secrets and Variables → Actions` y añadir:
   
   | Secret | Descripción |
   |--------|-------------|
   | `GOOGLE_CREDENTIALS_JSON` | JSON completo de la cuenta de servicio |
   | `GOOGLE_SHEET_ID` | ID del Google Sheet destino |

3. **Ejecución Manual**
   
   Navegar a `Actions → Wallapop Scraper Automation → Run workflow`

## Configuración

### Grupos de Concesionarios

El sistema procesa concesionarios en grupos organizados para rendimiento óptimo:

**Grupo 1 (Pequeños):** DURSAN D., Beatriz D., GESTICAR G., Garage Club C.  
**Grupo 2 (Medianos):** Red MundiCars, OCASIONPLUS, Red CRESTANEVADA  
**Grupo 3 (Grandes):** GRUPO O., INTEGRAL MOTION, FlexCar, concesionarios de alto volumen

### Modos de Ejecución

| Modo | Activación | Alcance |
|------|------------|---------|
| **Producción** | Programación diaria | Todos los 18+ concesionarios |
| **Prueba** | Activación manual | Un solo concesionario (DURSAN D.) |
| **Paralelo** | Workflow alternativo | Grupos 1-3 secuencialmente |

## Estructura de Datos

Los datos extraídos incluyen:

```
Marca, Modelo, Vendedor, Año, KM, Precio al Contado, Precio Financiado,
Tipo, Nº Plazas, Nº Puertas, Combustible, Potencia, Conducción, URL, Fecha Extracción
```

**Formatos de Salida:**
- Google Sheets (datos en vivo)
- Archivos Excel (backup local)
- Hojas individuales por vendedor

## Detalles Técnicos

### Configuración del Navegador

Configuración optimizada de Chrome para el entorno GitHub Actions:
- Modo headless con pantalla virtual
- Optimizaciones agresivas de rendimiento
- Carga de imágenes deshabilitada
- Huella de memoria reducida

### Manejo de Errores

- Reintentos automáticos para extracciones fallidas
- Gestión elegante de timeouts
- Sistema integral de logging
- Estrategias de extracción de respaldo

### Optimizaciones de Rendimiento

- Capacidades de procesamiento concurrente
- Navegación DOM eficiente
- Tiempos de espera mínimos entre solicitudes
- Manejo inteligente de paginación

## Monitoreo

### Logs de Ejecución
Logs de procesamiento en tiempo real disponibles en la interfaz de GitHub Actions

### Métricas de Éxito
- Tasa de finalización de extracción
- Resultados de validación de datos
- Análisis de tiempo de rendimiento
- Reportes de clasificación de errores

### Sistema de Backup
- Generación automática de Excel
- Retención de artifacts por 30 días
- Integración con control de versiones
- Procedimientos de recuperación

## Estructura del Proyecto

```
wallapop_coches_scraper/
├── .github/workflows/          # Automatización CI/CD
│   ├── scraper.yml            # Workflow principal
│   └── scraper_paralelo.yml   # Ejecución paralela
├── src/                       # Código fuente
│   ├── COCHES_SCR.py         # Scraper principal
│   ├── config.py             # Configuración
│   └── google_sheets_uploader.py
├── credentials/               # Autenticación
├── resultados/               # Archivos de salida
└── requirements.txt          # Dependencias
```

## Mantenimiento

### Actualizaciones Automáticas
- Gestión de dependencias vía Dependabot
- Parches de seguridad a través de GitHub
- Mantenimiento de compatibilidad del navegador

### Intervenciones Manuales
- Revisión trimestral de lista de concesionarios
- Optimización anual de rendimiento
- Actualizaciones de selectores según necesidad

## Contribución

Este es un proyecto comercial privado. Para consultas técnicas, usar GitHub Issues.

---

**Desarrollado por Carlos Peraza** • **Versión 12.3** • **Agosto 2025**
