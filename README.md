<div align="center">

# Plataforma de Automatización Datos de Coches Wallapop

![Build Status](https://github.com/B4TE5/wallapop_coches_scraper/workflows/Wallapop%20Scraper%20Automation/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11+-2b5b84.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-Integrado-34a853.svg)

### Sistema empresarial de extracción y análisis automatizado de datos vehiculares

</div>

---

## Descripción General

**Plataforma de Automatización de Datos Vehiculares Wallapop** es una solución empresarial diseñada para extraer, procesar y organizar sistemáticamente datos de inventario vehicular de concesionarios profesionales en el marketplace de Wallapop. El sistema opera de forma completamente autónoma, proporcionando inteligencia de mercado en tiempo real a través de pipelines de datos automatizados.

### Capacidades Principales

- **Extracción Automatizada de Datos**: Monitoreo continuo de más de 15 concesionarios vehiculares profesionales
- **Procesamiento en Tiempo Real**: Extracción y procesamiento diario de más de 5.000 anuncios vehiculares
- **Integración Cloud**: Exportación directa a Google Sheets con formato automatizado
- **Operación Sin Mantenimiento**: Ejecución completamente autónoma mediante infraestructura GitHub Actions

---

## Arquitectura Técnica

<details>
<summary><strong>Componentes del Sistema</strong></summary>

```
Entorno de Producción
├── GitHub Actions (Pipeline CI/CD)
├── Python 3.11 (Motor de Procesamiento)
├── Selenium WebDriver (Automatización de Navegador)
├── Google Sheets API (Almacenamiento de Datos)
└── Chrome Headless (Motor de Renderizado)
```

</details>

### Pipeline de Procesamiento de Datos

1. **Monitoreo de Fuentes**: Escaneo automatizado de perfiles de concesionarios configurados
2. **Extracción de Contenido**: Recuperación sistemática de especificaciones vehiculares y precios
3. **Normalización de Datos**: Estandarización de formatos, divisas y clasificaciones
4. **Validación de Calidad**: Verificación automatizada de completitud y precisión de datos
5. **Exportación Cloud**: Subida directa al espacio de trabajo Google Sheets designado
6. **Generación de Backups**: Artifacts Excel automatizados para redundancia de datos

---

## Configuración

### Prerrequisitos

- Repositorio GitHub con Actions habilitado
- Proyecto Google Cloud Platform con acceso a Sheets API
- Credenciales de cuenta de servicio con permisos apropiados

### Instrucciones de Configuración

<details>
<summary><strong>1. Configuración Google Cloud</strong></summary>

```bash
# Habilitar APIs requeridas
gcloud services enable sheets.googleapis.com
gcloud services enable drive.googleapis.com

# Crear cuenta de servicio
gcloud iam service-accounts create wallapop-scraper-bot \
    --display-name="Cuenta de Servicio Wallapop Scraper"
```

</details>

<details>
<summary><strong>2. Configuración GitHub Secrets</strong></summary>

Navegar a: `Configuración del Repositorio → Secrets and Variables → Actions`

Secrets requeridos:
- `GOOGLE_CREDENTIALS_JSON`: Credenciales JSON completas de la cuenta de servicio
- `GOOGLE_SHEET_ID`: Identificador del documento Google Sheets objetivo

</details>

<details>
<summary><strong>3. Configuración Google Sheets</strong></summary>

1. Crear nuevo documento Google Sheets
2. Compartir con email de cuenta de servicio (permisos de Editor)
3. Extraer Sheet ID de la URL del documento
4. Configurar como secret `GOOGLE_SHEET_ID`

</details>

---

## Operación

### Ejecución Automatizada

El sistema opera con **programación diaria a las 08:00 UTC** sin requerir intervención manual.

### Ejecución Manual

Acceso mediante interfaz GitHub Actions:
```
Repositorio → Actions → Wallapop Scraper Automation → Run workflow
```

**Modo Prueba**: Habilitar para validación de alcance limitado (un solo concesionario)  
**Modo Producción**: Extracción completa de todos los concesionarios configurados

---

## Salida de Datos

### Estructura Google Sheets

Las hojas diarias se generan automáticamente con formato: `SCR DD/MM/YY`

**Esquema de Datos:**
| Columna | Tipo | Descripción |
|---------|------|-------------|
| Marca | String | Fabricante del vehículo |
| Modelo | String | Designación completa del modelo |
| Vendedor | String | Identificación del concesionario |
| Año | Integer | Año de fabricación |
| KM | String | Kilometraje (formateado) |
| Precio al Contado | String | Precio al contado |
| Precio Financiado | String | Precio financiado |
| Combustible | String | Tipo de combustible |
| URL | String | URL del anuncio fuente |
| Fecha Extracción | Date | Timestamp de procesamiento |

### Métricas de Rendimiento

- **Capacidad de Procesamiento**: Más de 5.000 anuncios por ejecución
- **Precisión de Extracción**: Más del 95% de completitud de datos
- **Tiempo de Ejecución**: 2-4 horas (ejecución completa de producción)
- **Fiabilidad**: Más del 99% de tasa de finalización exitosa

---

## Red de Concesionarios

El alcance actual de monitoreo incluye **18 concesionarios profesionales** en toda España:

<details>
<summary><strong>Grupo 1 - Concesionarios Principales</strong></summary>

- DURSAN D. (~50 anuncios)
- Beatriz D. (~100 anuncios) 
- GESTICAR G. (~200 anuncios)
- Garage Club C. (~150 anuncios)

</details>

<details>
<summary><strong>Grupo 2 - Concesionarios Secundarios</strong></summary>

- Red MundiCars (~800 anuncios)
- OCASIONPLUS E. (~1.500 anuncios)
- Red CRESTANEVADA (~1.200 anuncios)

</details>

<details>
<summary><strong>Grupo 3 - Concesionarios de Gran Volumen</strong></summary>

- GRUPO O. (~2.000+ anuncios)
- INTEGRAL MOTION (~1.000 anuncios)
- Concesionarios regionales adicionales

</details>

---

## Monitoreo del Sistema

### Logs de Ejecución
Logs de procesamiento en tiempo real disponibles mediante la interfaz GitHub Actions con seguimiento detallado paso a paso de la ejecución.

### Manejo de Errores
Mecanismos comprensivos de recuperación de errores incluyendo:
- Lógica de reintento automático para extracciones fallidas
- Manejo elegante de timeouts de red
- Protocolos de validación y corrección de datos

### Sistemas de Backup
- **Exportaciones Excel automatizadas** retenidas durante 30 días
- **Control de versiones** de todos los cambios de configuración
- **Capacidades de rollback** para recuperación del sistema

---

## Mantenimiento

### Actualizaciones del Sistema
- **Actualizaciones automáticas de dependencias** mediante Dependabot
- **Gestión de parches de seguridad** a través de GitHub Actions
- **Compatibilidad de navegador** mantenida automáticamente

### Gestión de Configuración
Todas las configuraciones de concesionarios gestionadas mediante archivos de configuración con control de versiones con seguimiento de cambios y flujos de trabajo de aprobación.

---

## Soporte y Documentación

### Soporte Técnico
- **Seguimiento de Issues**: GitHub Issues con triage automatizado
- **Documentación**: Documentación comprehensiva inline en el código
- **Registro de Cambios**: Historial detallado de versiones y notas de release

### Información de Contacto
Para consultas técnicas o solicitudes de modificación del sistema, utilizar el sistema GitHub Issues.

---

## Licencia

Este proyecto es software propietario desarrollado para operaciones comerciales internas. Todos los derechos reservados.

---

<div align="center">

**Plataforma de Automatización de Datos Vehiculares Wallapop**  
*MOTICK.COM*

Versión 12.3 • Última Actualización: Agosto 2025

</div>
