<div align="center">

# 🚗 CAR SCRAPER 🚗

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
