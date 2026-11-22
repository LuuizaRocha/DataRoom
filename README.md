#  Data Room Intelligence Suite


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.x-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Pandas-Data%20Processing-green.svg" alt="Pandas">
  <img src="https://img.shields.io/badge/Pytest-Automated%20Testing-orange.svg" alt="Pytest">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey.svg" alt="License">
</p>

---

##  Architectural Overview

**Data Room** is a modular, production-ready analytical web application engineered in Python and powered by Streamlit. It provides a robust pipeline for end-to-end dataset lifecycle management—encompassing strict data ingestion, programmatic data cleaning, granular exploration, statistical profiling, and multi-format export capabilities.

---

##  Core Modules & Capabilities

* **Ingestion Layer (`core/importer.py`):** Secure payload parsing with structural integrity checks for tabular formats (CSV).
* **Sanitization Engine (`core/cleaner.py`):** Algorithmic mitigation of missing values, duplicate row dropping, and deterministic type casting.
* **Exploratory Analytics (`core/explorer.py` & `analytics.py`):** High-performance filtering, slicing, and descriptive statistical aggregation.
* **Export Pipeline (`core/exporter.py`):** Streamlined serialization and egress of processed frames.
* **Test Suite (`tests/`):** Comprehensive unit coverage using `pytest` to guarantee component reliability.

---

##  Technology Stack

* **Language:** Python
* **Interface:** Streamlit[cite: 1]
* **Data Manipulation:** Pandas, NumPy
* **Testing Framework:** Pytest[cite: 1]

---

##  Local Deployment Guide

### Prerequisites
* Python `3.8` or higher installed on your system.
* Pip package manager.

### Step-by-Step Installation

1. **Clone or navigate to the repository directory:**
   ```bash
   cd DATA-ROOM
   pip install -r requirements.txt
   python -m streamlit run app.py
