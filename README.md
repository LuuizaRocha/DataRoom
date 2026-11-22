<div align="center">

# ◈ DATA ROOM

### DATA ANALYSIS & CLEANING WORKSPACE

**Turn raw data into reliable insights.**

A session-based workspace to import, inspect, clean, analyze and export tabular data — built with Python and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-8FB9E8)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-2EA44F)]()

</div>

---

## Overview

DATA ROOM is a data analysis and cleaning workspace designed to make everyday data preparation clearer and more approachable. Import CSV or Excel files, automatically profile data quality, explore records, preview cleaning transformations, build interactive visualizations and export your results.

The application runs as a Streamlit web app. Data processing is performed in the active app session; no database is required.

> **Designed for analysts, students and curious builders who want a clean workflow from raw tables to useful insights.**

## Features

| Workspace | What you can do |
|---|---|
| **Overview** | Review dataset size, data quality score, missing values, duplicates and column profiles. |
| **Import Data** | Upload CSV, TSV, XLSX or XLS files (delimiter, encoding, Brazilian decimal commas and worksheet are handled for you), preview the contents or load the sample dataset. |
| **Data Explorer** | Search across columns, stack multiple filters (text, numbers, dates, missing values), download the filtered view and inspect column-level statistics. |
| **Data Cleaning** | Handle missing values, remove duplicates, trim whitespace, standardize text and convert data types. |
| **Analytics** | Explore descriptive statistics, numeric distributions, trends over time, category frequencies and correlations. |
| **Export Center** | Download the working copy or the original import as CSV or Excel, optionally with a change-log sheet. |

### Data quality & safe cleaning

- Automatic column profiling: inferred type, non-null count, missing percentage, unique values and sample values.
- Data Quality Score based on completeness and row uniqueness.
- Preview transformations before applying them.
- Undo the latest cleaning operation.
- Compare the original imported dataset with the current working copy.
- The original dataset is kept separately and is not modified by cleaning actions.

### User experience

- Light, Dark and System appearance (app menu → Settings → Theme), driven by Streamlit's native theming so tables and charts always match.
- A single typeface (Inter) across text, widgets, tables and charts.
- Native multipage navigation with a dedicated page per workspace.
- Built-in sample retail dataset.
- Clear validation and error messages.
- Session-based workflow with no database setup.

## Preview

The palette is defined once in `.streamlit/config.toml` (one block per appearance mode).

| Dark workspace | Light workspace |
|---|---|
| Midnight `#101827` | Mist `#F4F6FA` |
| Slate `#1C2B40` | Cloud `#DCE7F3` |
| Ice `#8FB9E8` | Blue accent |

*Screenshots can be added to `assets/screenshots/` and linked here as the project evolves.*

## Tech stack

- **Python** — application logic
- **Streamlit** — interactive web interface
- **Pandas** — tabular data manipulation
- **NumPy** — numerical operations
- **Plotly** — interactive charts
- **OpenPyXL** — Excel export and workbook support
- **Pytest** — automated tests

## Project structure

```text
DATA-ROOM/
├── .streamlit/config.toml     # theme (light + dark), font, toolbar
├── assets/                    # logo and brand assets
├── components/                # reusable UI: layout, metrics, tables, charts, sidebar, styles
├── core/                      # pure pandas logic (no Streamlit): importer, cleaner, explorer, ...
├── data/sample_dataset.csv
├── tests/                     # unit tests + end-to-end app tests (Streamlit AppTest)
├── views/                     # one file per workspace page
│   ├── overview.py
│   ├── import_data.py
│   ├── data_explorer.py
│   ├── data_cleaning.py
│   ├── analytics.py
│   └── export_center.py
├── app.py                     # entry point: page setup + navigation
├── config.py                  # constants
├── state.py                   # session state: load, commit, undo, restore
├── requirements.txt
└── requirements-dev.txt
```

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/DATA-ROOM.git
cd DATA-ROOM
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Launch DATA ROOM

```bash
streamlit run app.py
```

The app will open in your browser, usually at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Sign in with GitHub and select **Create app**.
4. Choose your repository and branch.
5. Set the main file path to `app.py`.
6. Select **Deploy**.

Streamlit Community Cloud installs the dependencies listed in `requirements.txt`.

## Run tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The suite includes end-to-end tests that drive the real app headlessly (every page, filters, cleaning, undo).

## Data handling & privacy

DATA ROOM does not require a database. Uploaded files are read into the running app session and processed in memory. The original import is kept separately from the working dataset during that session.

**Important:** on Streamlit Community Cloud, uploaded data is transmitted to the hosted application. Session state is not permanent storage and can be cleared when a session ends or the app restarts. Do not upload confidential, personally identifiable, medical or otherwise regulated data to a public deployment.

## Current scope & limitations

- This version is designed for tabular CSV and Excel workflows.
- Cleaning keeps the last 10 steps undoable to bound memory use.
- Session data is temporary; there is no account system or persistent project storage.
- Very large datasets may require additional memory and processing time.
- CSV type inference and automatic delimiter detection may need manual review for unusual files.
- Data Quality Score is a practical indicator, not a formal certification of data quality.

## Roadmap

- [ ] Downloadable data quality report
- [ ] Rename / drop column operations
- [ ] More date and currency cleaning utilities
- [ ] Configurable quality scoring
- [ ] Persistent project storage (optional backend)
- [ ] Additional chart types and cross-tab analysis
- [ ] Expanded test coverage and CI workflow

## Contributing

Issues and pull requests are welcome. For substantial changes, open an issue first to discuss the proposed improvement.

## License

Distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">

**DATA ROOM** · Built with Python, Streamlit and curiosity.

*Make your data make sense.*

</div>
