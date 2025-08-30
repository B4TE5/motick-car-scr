# Wallapop Car Scraper

**Automated data extraction system for professional car dealers on Wallapop marketplace**

[![Build](https://img.shields.io/badge/Build-Passing-success)](https://github.com/your-repo/wallapop-scraper) [![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org) [![License](https://img.shields.io/badge/License-Private-red)](LICENSE)

## 📊 Live Data Dashboard

**View extracted data:** [Google Sheets Dashboard](https://docs.google.com/spreadsheets/d/1drZonCFIP5BFuhbUW9cUauDQOWIVpE0V7P2ErpJq6bM/edit?gid=265284675#gid=265284675)

---

## Overview

This system monitors 18+ professional car dealers on Wallapop, extracting and organizing vehicle inventory data automatically. Built for scalability and reliability with zero manual intervention required.

**Key Metrics:**
- **5,000+** vehicles processed daily
- **95%+** data completeness rate
- **3-hour** execution window
- **Daily** automated runs at 08:00 UTC

## Architecture

```
GitHub Actions → Python Engine → Selenium WebDriver → Data Processing → Google Sheets
```

**Core Components:**
- **Python 3.11** processing engine
- **Selenium WebDriver** with Chrome headless
- **Google Sheets API** for data storage
- **GitHub Actions** for automation
- **Excel backups** with 30-day retention

## Quick Start

### Prerequisites

- GitHub repository with Actions enabled
- Google Cloud project with Sheets API enabled
- Service account with appropriate permissions
- Google Sheet with sharing permissions

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/wallapop-scraper.git
   cd wallapop-scraper
   ```

2. **Configure GitHub Secrets**
   
   Go to `Settings → Secrets and Variables → Actions` and add:
   
   | Secret | Description |
   |--------|-------------|
   | `GOOGLE_CREDENTIALS_JSON` | Complete service account JSON |
   | `GOOGLE_SHEET_ID` | Target Google Sheet ID |

3. **Manual Execution**
   
   Navigate to `Actions → Wallapop Scraper Automation → Run workflow`

## Configuration

### Dealer Groups

The system processes dealers in organized groups for optimal performance:

**Group 1 (Small):** DURSAN D., Beatriz D., GESTICAR G., Garage Club C.  
**Group 2 (Medium):** MundiCars network, OCASIONPLUS, CRESTANEVADA network  
**Group 3 (Large):** GRUPO O., INTEGRAL MOTION, FlexCar, high-volume dealers

### Execution Modes

| Mode | Trigger | Scope |
|------|---------|-------|
| **Production** | Daily schedule | All 18+ dealers |
| **Test** | Manual trigger | Single dealer (DURSAN D.) |
| **Parallel** | Alternative workflow | Groups 1-3 sequentially |

## Data Structure

Extracted data includes:

```
Marca, Modelo, Vendedor, Año, KM, Precio al Contado, Precio Financiado,
Tipo, Nº Plazas, Nº Puertas, Combustible, Potencia, Conducción, URL, Fecha Extracción
```

**Output Formats:**
- Google Sheets (live data)
- Excel files (local backup)
- Individual seller sheets

## Technical Details

### Browser Configuration

Optimized Chrome setup for GitHub Actions environment:
- Headless mode with virtual display
- Aggressive performance optimizations
- Image loading disabled
- Reduced memory footprint

### Error Handling

- Automatic retries for failed extractions
- Graceful timeout management
- Comprehensive logging system
- Fallback extraction strategies

### Performance Optimizations

- Concurrent processing capabilities
- Efficient DOM traversal
- Minimal wait times between requests
- Smart pagination handling

## Monitoring

### Execution Logs
Real-time processing logs available in GitHub Actions interface

### Success Metrics
- Extraction completion rate
- Data validation results
- Performance timing analysis
- Error classification reports

### Backup System
- Automated Excel generation
- 30-day artifact retention
- Version control integration
- Recovery procedures

## Project Structure

```
wallapop_coches_scraper/
├── .github/workflows/          # CI/CD automation
│   ├── scraper.yml            # Main workflow
│   └── scraper_paralelo.yml   # Parallel execution
├── src/                       # Source code
│   ├── COCHES_SCR.py         # Main scraper
│   ├── config.py             # Configuration
│   └── google_sheets_uploader.py
├── credentials/               # Authentication
├── resultados/               # Output files
└── requirements.txt          # Dependencies
```

## Maintenance

### Automated Updates
- Dependency management via Dependabot
- Security patches through GitHub
- Browser compatibility maintenance

### Manual Interventions
- Quarterly dealer list review
- Annual performance optimization
- Selector updates as needed

## Contributing

This is a private commercial project. For technical inquiries, please use GitHub Issues.

---

**Developed by Carlos Peraza** • **Version 12.3** • **August 2025**
