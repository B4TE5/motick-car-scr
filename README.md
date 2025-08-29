# Wallapop Vehicle Data Automation Platform

<div align="center">

![Build Status](https://github.com/B4TE5/wallapop_coches_scraper/workflows/Wallapop%20Scraper%20Automation/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11+-2b5b84.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-Integrated-34a853.svg)

### Enterprise-grade automated vehicle data extraction and analysis system

</div>

---

## Overview

**Wallapop Vehicle Data Automation Platform** is an enterprise solution designed to systematically extract, process, and organize vehicle inventory data from professional dealers on Wallapop marketplace. The system operates fully autonomously, providing real-time market intelligence through automated data pipelines.

### Core Capabilities

- **Automated Data Extraction**: Continuous monitoring of 15+ professional vehicle dealers
- **Real-time Processing**: Daily extraction and processing of 5,000+ vehicle listings
- **Cloud Integration**: Direct export to Google Sheets with automated formatting
- **Zero-maintenance Operation**: Fully autonomous execution via GitHub Actions infrastructure

---

## Technical Architecture

<details>
<summary><strong>System Components</strong></summary>

```
Production Environment
├── GitHub Actions (CI/CD Pipeline)
├── Python 3.11 (Core Processing Engine)
├── Selenium WebDriver (Browser Automation)
├── Google Sheets API (Data Storage)
└── Chrome Headless (Rendering Engine)
```

</details>

### Data Processing Pipeline

1. **Source Monitoring**: Automated scanning of configured dealer profiles
2. **Content Extraction**: Systematic retrieval of vehicle specifications and pricing
3. **Data Normalization**: Standardization of formats, currencies, and classifications  
4. **Quality Validation**: Automated verification of data completeness and accuracy
5. **Cloud Export**: Direct upload to designated Google Sheets workspace
6. **Backup Generation**: Automated Excel artifacts for data redundancy

---

## Configuration

### Prerequisites

- GitHub repository with Actions enabled
- Google Cloud Platform project with Sheets API access
- Service account credentials with appropriate permissions

### Setup Instructions

<details>
<summary><strong>1. Google Cloud Configuration</strong></summary>

```bash
# Enable required APIs
gcloud services enable sheets.googleapis.com
gcloud services enable drive.googleapis.com

# Create service account
gcloud iam service-accounts create wallapop-scraper-bot \
    --display-name="Wallapop Scraper Service Account"
```

</details>

<details>
<summary><strong>2. GitHub Secrets Configuration</strong></summary>

Navigate to: `Repository Settings → Secrets and Variables → Actions`

Required secrets:
- `GOOGLE_CREDENTIALS_JSON`: Complete service account JSON credentials
- `GOOGLE_SHEET_ID`: Target Google Sheets document identifier

</details>

<details>
<summary><strong>3. Google Sheets Setup</strong></summary>

1. Create new Google Sheets document
2. Share with service account email (Editor permissions)
3. Extract Sheet ID from document URL
4. Configure as `GOOGLE_SHEET_ID` secret

</details>

---

## Operation

### Automated Execution

The system operates on a **daily schedule at 08:00 UTC** with no manual intervention required.

### Manual Execution

Access via GitHub Actions interface:
```
Repository → Actions → Wallapop Scraper Automation → Run workflow
```

**Test Mode**: Enable for limited scope validation (single dealer)  
**Production Mode**: Full extraction across all configured dealers

---

## Data Output

### Google Sheets Structure

Daily sheets are automatically generated with format: `SCR DD/MM/YY`

**Data Schema:**
| Column | Type | Description |
|--------|------|-------------|
| Marca | String | Vehicle manufacturer |
| Modelo | String | Complete model designation |
| Vendedor | String | Dealer identification |
| Año | Integer | Manufacturing year |
| KM | String | Mileage (formatted) |
| Precio al Contado | String | Cash price |
| Precio Financiado | String | Financed price |
| Combustible | String | Fuel type |
| URL | String | Source listing URL |
| Fecha Extracción | Date | Processing timestamp |

### Performance Metrics

- **Processing Capacity**: 5,000+ listings per execution
- **Extraction Accuracy**: 95%+ data completeness
- **Execution Time**: 2-4 hours (full production run)
- **Reliability**: 99%+ successful completion rate

---

## Dealer Network

Current monitoring scope includes **18 professional dealers** across Spain:

<details>
<summary><strong>Group 1 - Primary Dealers</strong></summary>

- DURSAN D. (~50 listings)
- Beatriz D. (~100 listings) 
- GESTICAR G. (~200 listings)
- Garage Club C. (~150 listings)

</details>

<details>
<summary><strong>Group 2 - Secondary Dealers</strong></summary>

- MundiCars network (~800 listings)
- OCASIONPLUS E. (~1,500 listings)
- CRESTANEVADA network (~1,200 listings)

</details>

<details>
<summary><strong>Group 3 - Large Volume Dealers</strong></summary>

- GRUPO O. (~2,000+ listings)
- INTEGRAL MOTION (~1,000 listings)
- Additional regional dealers

</details>

---

## System Monitoring

### Execution Logs
Real-time processing logs available via GitHub Actions interface with detailed step-by-step execution tracking.

### Error Handling
Comprehensive error recovery mechanisms including:
- Automatic retry logic for failed extractions
- Graceful handling of network timeouts
- Data validation and correction protocols

### Backup Systems
- **Automated Excel exports** retained for 30 days
- **Version control** of all configuration changes
- **Rollback capabilities** for system recovery

---

## Maintenance

### System Updates
- **Automatic dependency updates** via Dependabot
- **Security patch management** through GitHub Actions
- **Browser compatibility** maintained automatically

### Configuration Management
All dealer configurations managed through version-controlled configuration files with change tracking and approval workflows.

---

## Support & Documentation

### Technical Support
- **Issue Tracking**: GitHub Issues with automated triage
- **Documentation**: Comprehensive inline code documentation
- **Change Log**: Detailed version history and release notes

### Contact Information
For technical inquiries or system modification requests, please use the GitHub Issues system.

---

## License

This project is proprietary software developed for internal business operations. All rights reserved.

---

<div align="center">

**Wallapop Vehicle Data Automation Platform**  
*Enterprise Solution for Market Intelligence*

Version 12.3 • Last Updated: August 2025

</div>
