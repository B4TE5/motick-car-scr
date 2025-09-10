<div align="center">

# 🚗 Wallapop Car Scraper 🚗

**Sistema automatizado de extracción de datos para concesionarios en Wallapop**

[![Build](https://img.shields.io/badge/Build-Passing-success)](../../actions)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-43B02A)](https://www.selenium.dev/downloads/)
[![Google Sheets API](https://img.shields.io/badge/Google-Workspace-4285F4)](https://developers.google.com/workspace/sheets/api/guides/concepts?hl=es-419)
[![License](https://img.shields.io/badge/License-Private-red)](LICENSE)

</div>


---

## 🖥️ Descripción General

Este sistema monitorea 18 concesionarios profesionales en Wallapop, extrayendo y organizando datos de inventario de forma automática. Diseñado para escalabilidad y confiabilidad sin intervención manual.

### Métricas Clave

- **División por hojas:** dos hojas diarias generadas: `SCR.J1` y `SCR.J2`
- **Vehículos procesados:** casi **5.000** coches por hoja, diariamente
- **Completitud de datos:** superior al **95%**
- **Tiempo medio de ejecución:** aproximadamente **5 horas** por job en paralelo
- **Frecuencia:** ejecución automática diaria a las **06:00** (hora España)

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura de flujo automatizado, basada en GitHub Actions y servicios cloud:

### Componentes Técnicos

- **GitHub Actions**  
  Ejecución automática de workflows programados.

- **Python 3.11**  
  Motor principal del sistema: extracción, limpieza y transformación de datos.

- **Selenium WebDriver (Chrome Headless)**  
  Navegación automatizada y scraping de páginas de vendedores en Wallapop.

- **Google Sheets API**  
  Almacenamiento estructurado del inventario diario en hojas compartidas.


## 🚀 Inicio Rápido

### Requisitos Previos

- Un repositorio en **GitHub** con **Actions habilitado**
- Un proyecto en **Google Cloud** con la **API de Google Sheets** activada
- Una **cuenta de servicio** con permisos suficientes y credenciales JSON
- Un **Google Sheet compartido** con la cuenta de servicio

### Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/TU-REPO/wallapop-car-scraper.git
   cd wallapop-scraper
   ```

2. **Configurar GitHub Secrets**
   
   Ir a `Settings → Secrets and Variables → Actions` y añadir:
   
   |  Secret|  Descripción|
   |--------|-------------|
   | `GOOGLE_CREDENTIALS_JSON` | JSON completo de la cuenta de servicio |
   | `GOOGLE_SHEET_ID` | ID del Google Sheet destino |

3. **Ejecución Manual**
   
   Navegar a `Actions → Wallapop Scraper Automation → Run workflow`

## ⚙️ Configuración del Sistema

### Organización de Concesionarios

Los concesionarios están distribuidos en tres grupos para optimizar la ejecución y equilibrar la carga:

| Grupo      | Clasificación     | Concesionarios incluidos                                              |
|------------|-------------------|------------------------------------------------------------------------|
| **Grupo 1** | Volumen bajo      | DURSAN D., Beatriz D., GESTICAR G., Garage Club C.                    |
| **Grupo 2** | Volumen medio     | Red MundiCars, OCASIONPLUS, Red CRESTANEVADA                          |
| **Grupo 3** | Volumen alto      | INTEGRAL MOTION, FlexCar   

### Modos de Ejecución

El sistema admite tres modos de ejecución, adaptados a distintos contextos operativos:

- **Producción:**  
  Ejecución programada diariamente a las 06:00 (hora España). Procesa automáticamente todos los concesionarios (más de 18) en una única ejecución secuencial.

- **Prueba:**  
  Ejecución manual para testeo. Cuenta con dos variantes:
  
  - **Prueba rápida:** procesa únicamente `DURSAN D.`, útil para validar el flujo general de scraping, subida y conexión.
  - **Prueba de extracción:** procesa tres concesionarios específicos con **formatos de precio distintos**, diseñada para verificar la robustez del sistema frente a variaciones en los datos.

- **Paralelo (Distribuido en Jobs):**  
  Utiliza un workflow alternativo con **dos jobs independientes (`job1` y `job2`)** que se ejecutan en paralelo dentro de GitHub Actions.  
  Cada job procesa distintos grupos de concesionarios, lo que permite reducir significativamente el tiempo total de ejecución.

## 🔍 Estructura de Datos

|  Atributo                 |  Descripción                              |
|-------------------------|---------------------------------------------|
| **Marca**               | Marca del vehículo                          |
| **Modelo**              | Modelo del vehículo                         |
| **Vendedor**            | Nombre del concesionario                    |
| **Año**                 | Año de matriculación                        |
| **KM**                  | Kilometraje                                 |
| **Precio al Contado**   | Precio del vehículo sin financiación        |
| **Precio Financiado**   | Precio con financiación                     |
| **Tipo**                | Tipo de vehículo (SUV, Berlina, etc.)       |
| **Nº Plazas**           | Número de plazas del vehículo               |
| **Nº Puertas**          | Número de puertas                           |
| **Combustible**         | Tipo de combustible (Gasolina, Diésel, etc.)|
| **Potencia**            | Potencia en caballos (CV)                   |
| **Conducción**          | Tipo de cambio: manual o automático         |
| **URL**                 | Enlace al anuncio original en Wallapop      |
| **Fecha Extracción**    | Fecha y hora en que se extrajo la información |


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
