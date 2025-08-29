# 🚗 Wallapop Coches Scraper Automation

<div align="center">

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Selenium](https://img.shields.io/badge/selenium-4.26.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-automated-brightgreen.svg)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-integrated-success.svg)

**Sistema automatizado para extraer datos de vehículos de vendedores profesionales en Wallapop**

[Características](#características) • [Instalación](#instalación) • [Configuración](#configuración) • [Uso](#uso) • [Resultados](#resultados)

</div>

---

## 📋 Descripción

**Wallapop Coches Scraper** es un sistema completamente automatizado que extrae información detallada de vehículos de vendedores profesionales específicos en Wallapop y los organiza automáticamente en Google Sheets.

### 🎯 ¿Qué hace?

- 🔍 **Extrae datos** de coches de vendedores específicos en Wallapop
- 📊 **Organiza automáticamente** la información en Google Sheets  
- ⏰ **Se ejecuta automáticamente** cada día a las 8:00 AM UTC
- 💾 **Crea backups** en Excel como artifacts
- 🔄 **Maneja errores** y reintentos automáticamente

---

## ✨ Características

### 🚀 **Automatización Completa**
- ⏰ Ejecución diaria automática con GitHub Actions
- 🤖 Sin intervención manual requerida
- ☁️ Infraestructura completamente en la nube

### 📊 **Datos Extraídos**
- 🏷️ **Marca y Modelo** completo del vehículo
- 💰 **Precios** (al contado y financiado)
- 📍 **Vendedor** y información de contacto
- 📅 **Año** de fabricación
- 🛣️ **Kilómetros** recorridos
- ⚙️ **Especificaciones técnicas** (combustible, potencia, transmisión)
- 🔗 **URL** del anuncio original

### 🔧 **Tecnologías**
- **Python 3.11+** para la lógica principal
- **Selenium WebDriver** para navegación web automatizada
- **Google Sheets API** para almacenamiento en la nube
- **GitHub Actions** para automatización y scheduling
- **Pandas** para procesamiento de datos
- **Chrome Headless** para scraping optimizado

---

## 🏗️ Arquitectura

```
wallapop_coches_scraper/
├── .github/workflows/
│   ├── scraper.yml              # Workflow principal
│   └── scraper_paralelo.yml     # Workflow paralelo
├── src/
│   ├── COCHES_SCR.py           # Scraper principal
│   ├── config.py               # Configuración de vendedores
│   └── google_sheets_uploader.py # Integración Google Sheets
├── requirements.txt             # Dependencias Python
└── README.md                   # Documentación
```

---

## ⚙️ Instalación

### 📋 **Prerrequisitos**

1. **Cuenta de GitHub** con GitHub Actions habilitado
2. **Google Cloud Project** con APIs habilitadas:
   - Google Sheets API
   - Google Drive API
3. **Google Sheets** para almacenar los datos

### 🔧 **Configuración Paso a Paso**

#### 1️⃣ **Clonar Repositorio**
```bash
git clone https://github.com/TU-USUARIO/wallapop_coches_scraper.git
cd wallapop_coches_scraper
```

#### 2️⃣ **Google Cloud Setup**
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita las APIs necesarias:
   - Google Sheets API
   - Google Drive API
4. Crea un Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Descarga las credenciales JSON

#### 3️⃣ **Google Sheets Setup**
1. Crea un nuevo Google Sheet
2. Comparte con el email del Service Account (permisos de Editor)
3. Copia el Sheet ID de la URL

#### 4️⃣ **GitHub Secrets**
En tu repositorio GitHub: Settings → Secrets and variables → Actions

Crea estos secrets:
- `GOOGLE_CREDENTIALS_JSON`: Contenido completo del archivo JSON de credenciales
- `GOOGLE_SHEET_ID`: ID de tu Google Sheet

---

## 🚀 Uso

### ⏰ **Ejecución Automática**
El sistema se ejecuta automáticamente **todos los días a las 8:00 AM UTC**.

### 🧪 **Ejecución Manual**
1. Ve a tu repositorio en GitHub
2. **Actions** → **Wallapop Scraper Automation**
3. **Run workflow** → Selecciona opciones → **Run workflow**

### 🔧 **Modos de Ejecución**

#### **Modo Prueba** 
- ✅ Marca "Modo de prueba" al ejecutar manualmente
- Extrae solo datos de DURSAN D. (rápido para testing)

#### **Modo Producción**
- ❌ NO marcar "Modo de prueba"
- Extrae TODOS los vendedores configurados
- Duración: ~2-4 horas dependiendo del volumen

---

## 📊 Resultados

### 📈 **Google Sheets**
Los datos se organizan automáticamente en:
- **Una hoja por día**: `SCR DD/MM/YY`
- **Todos los coches** de todos los vendedores en la misma hoja
- **Columnas organizadas**: Marca, Modelo, Vendedor, Año, KM, Precios, etc.

### 💾 **Backups Automáticos**
- **Excel files** disponibles como GitHub Artifacts
- **Retención**: 30 días
- **Descarga directa** desde GitHub Actions

### 📋 **Estadísticas Incluidas**
- Total de coches extraídos
- Éxito de extracción por vendedor  
- Porcentaje de precios capturados
- Timestamp de última actualización

---

## 🛠️ Vendedores Configurados

El sistema actualmente monitorea estos vendedores profesionales:

| Vendedor | Grupo | Coches Aprox. |
|----------|-------|---------------|
| DURSAN D. | 1 | ~50 |
| Beatriz D. | 1 | ~100 |
| GESTICAR G. | 1 | ~200 |
| MundiCars V. | 2 | ~800 |
| OCASIONPLUS E. | 2 | ~1500 |
| GRUPO O. | 3 | ~2000+ |

**Total estimado: ~5000+ vehículos monitoreados**

---

## ⚡ Optimizaciones

### 🚀 **Rendimiento**
- **Chrome headless** optimizado para velocidad
- **Timeouts inteligentes** para manejar cargas lentas
- **Scroll progresivo** para cargar todos los anuncios
- **Manejo de errores** con reintentos automáticos

### 🔄 **Escalabilidad**  
- **Ejecución paralela** disponible para mayor velocidad
- **Agrupación de vendedores** por volumen de datos
- **Limits configurables** de tiempo y reintentos

### 📱 **Compatibilidad**
- ✅ GitHub Actions (Ubuntu latest)
- ✅ Chrome/Chromium headless
- ✅ Python 3.11+
- ✅ Selenium 4.26+

---

## 🔍 Troubleshooting

### ❌ **Errores Comunes**

#### "Credentials not found"
- ✅ Verificar que `GOOGLE_CREDENTIALS_JSON` esté configurado
- ✅ El JSON debe estar en una sola línea

#### "Sheet not found"
- ✅ Verificar `GOOGLE_SHEET_ID` 
- ✅ Confirmar que el sheet está compartido con el service account

#### "Chrome binary not found"
- ✅ Normal en GitHub Actions, se instala automáticamente
- ✅ Verificar que `HEADLESS_MODE=true`

### 📞 **Soporte**
Si encuentras problemas, revisa:
1. **GitHub Actions logs** para errores detallados
2. **Google Sheets** para verificar permisos
3. **Issues** en este repositorio

---

## 📈 Roadmap

### 🎯 **Próximas Mejoras**
- [ ] Dashboard web para visualizar estadísticas
- [ ] Alertas por email cuando termine/falle
- [ ] Filtros por marca, precio, año
- [ ] Análisis de tendencias de precios
- [ ] API REST para consultar datos
- [ ] Notificaciones cuando aparezcan coches específicos

### 🔮 **Features Avanzados**
- [ ] Machine Learning para predecir precios
- [ ] Comparativas automáticas entre vendedores  
- [ ] Detección de ofertas especiales
- [ ] Integración con más plataformas de venta

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. **Fork** el proyecto
2. Crea tu **feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la branch (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

---

## ⭐ ¿Te resultó útil?

Si este proyecto te ayudó, considera:
- ⭐ **Darle una estrella** en GitHub
- 🐛 **Reportar bugs** en Issues
- 💡 **Sugerir mejoras** en Discussions

---

<div align="center">

**Desarrollado con ❤️ para automatizar la búsqueda de vehículos**

[⬆ Volver arriba](#-wallapop-coches-scraper-automation)

</div>
