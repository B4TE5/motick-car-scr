<div align="center">

# 🚗 Wallapop Car Scraper 🚗

**Sistema automatizado de extracción de datos para concesionarios profesionales en Wallapop**

[![Build](https://img.shields.io/badge/Build-Passing-success)](../../actions)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-43B02A)](https://www.selenium.dev/downloads/)
[![Google Sheets API](https://img.shields.io/badge/Google-Workspace-4285F4)](https://developers.google.com/workspace/sheets/api/guides/concepts?hl=es-419)
[![License](https://img.shields.io/badge/License-Private-red)](LICENSE)

## Excel de Datos Diario

🔗 [Google Sheets Link](https://docs.google.com/spreadsheets/d/1drZonCFIP5BFuhbUW9cUauDQOWIVpE0V7P2ErpJq6bM/edit?gid=265284675#gid=265284675)

</div>


---

## 🖥️ Descripción General

Este sistema monitorea más de 18 concesionarios profesionales en Wallapop, extrayendo y organizando datos de inventario vehicular de forma automática. Diseñado para escalabilidad y confiabilidad sin intervención manual.

### 📊 Métricas Clave

- **División por hojas:** dos hojas diarias generadas: `SCR.J1` y `SCR.J2`
- **Vehículos procesados:** casi **5.000** coches por hoja, diariamente
- **Completitud de datos:** superior al **95%**
- **Tiempo medio de ejecución:** aproximadamente **5 horas** por job en paralelo
- **Frecuencia:** ejecución automática diaria a las **06:00** (hora España)

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura de flujo automatizado, basada en GitHub Actions y servicios cloud:


### Componentes Técnicos

- **GitHub Actions**  
  Orquestación y ejecución automática de workflows programados.

- **Python 3.11**  
  Motor principal del sistema: extracción, limpieza y transformación de datos.

- **Selenium WebDriver (Chrome Headless)**  
  Navegación automatizada y scraping de páginas de vendedores en Wallapop.

- **Google Sheets API**  
  Almacenamiento estructurado del inventario diario en hojas compartidas.


## 🚀 Inicio Rápido

### Requisitos Previos

- Repositorio GitHub con Actions habilitado
- Proyecto Google Cloud con API de Sheets habilitada
- Cuenta de servicio con permisos apropiados
- Google Sheet con permisos de compartición

### Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/TU-REPO/wallapop-car-scraper.git
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

## ⚙️ Configuración

### Grupos de Concesionarios

El sistema procesa concesionarios en grupos organizados para rendimiento óptimo:

- **Grupo 1 (Pequeños):** DURSAN D., Beatriz Dursan., GESTICAR G., Garage Club C.  
- **Grupo 2 (Medianos):** Red MundiCars, OCASIONPLUS, Red CRESTANEVADA  
- **Grupo 3 (Grandes):** INTEGRAL MOTION, FlexCar

### Modos de Ejecución

| Modo | Activación | Alcance |
|------|------------|---------|
| **Producción** | Programación diaria | Todos los 18+ concesionarios |
| **Prueba** | Activación manual | Un solo concesionario (DURSAN D.) |
| **Paralelo** | Workflow alternativo | Grupos 1-3 secuencialmente |

## 🔍 Estructura de Datos

| Campo               | Descripción                           |
|---------------------|---------------------------------------|
| **Marca**           | Marca del vehículo                   |
| **Modelo**          | Modelo del vehículo                  |
| **Vendedor**        | Nombre del vendedor                  |
| **Año**             | Año de matriculación                 |
| **KM**              | Kilometraje                          |
| **Precio al Contado** | Precio sin financiación             |
| **Precio Financiado** | Precio con financiación             |
| **Tipo**            | Tipo de vehículo                     |
| **Nº Plazas**       | Número de plazas                     |
| **Nº Puertas**      | Número de puertas                    |
| **Combustible**     | Tipo de combustible                  |
| **Potencia**        | Potencia en CV                       |
| **Conducción**      | Manual/Automática                    |
| **URL**             | Enlace al anuncio en Wallapop        |
| **Fecha Extracción**| Fecha en que se extrajo la información|

###  📞 Contacto
> Para consultas técnicas utilizar sistema **GitHub Issues**

---

## 📄 Licencia

> **Software Propietario** - Desarrollado para operaciones comerciales internas
> Todos los derechos reservados

---

<div align="center">

**Desarrollado por:** Carlos Peraza  
**Versión:** 12.6 • **Fecha:** Agosto 2025

[![motick.com](https://img.shields.io/badge/motick.com-00f1a2?style=for-the-badge&labelColor=2d3748)](https://www.motick.com/)

*Sistema de extracción automatizada para operaciones comerciales*

**© 2025- Todos los derechos reservados**

</div>
