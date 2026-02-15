# Data_Cleaning_Agent
Enterprise-grade automated data quality and cleaning platform powered by LLM-driven planning and deterministic execution.

## Overview
Data_Cleaning_Agent is a modular data quality system that separates LLM-based decision making from deterministic execution to ensure transparency, auditability, and controlled transformations.
The system:
Profiles datasets
Generates structured cleaning plans using an LLM
Applies transformations programmatically
Tracks transformation impact
Logs every modification
Provides a professional Streamlit dashboard

## Architecture
Streamlit UI
      ↓
FastAPI Backend
      ↓
LLMDataCleaningAgent (Orchestrator)
 ├─ DataProfiler
 ├─ LLMPlanner
 └─ ExecutionEngine
      ↓
Cleaned Dataset + Audit Log

## Core Capabilities
### Schema Standardization
Numeric normalization
Robust multi-format date parsing
Boolean conversion
State code to full state name mapping
Tracks rows changed per column

### Missing Value Handling
Mean / Median for numeric columns
Mode (applied only if ≥ 90% dominance)
Missing value flagging
No row deletion

### Duplicate Handling
Removes exact full-row duplicates only
Logs rows removed

### Outlier Detection
IQR-based detection
Flags anomalies without removing data
Adds _outlier_flag columns

### Project Structure
app/
 ├─ agents/
 │   ├─ profiler.py
 │   ├─ planner.py
 │   ├─ executor.py
 │   └─ orchestrator.py
 ├─ services/
 │   └─ llm_service.py
 └─ main.py

data/
 ├─ raw/
 └─ cleaned/

streamlit_app.py
requirements.txt
README.md

## Running the Project
### Install Dependencies
pip install -r requirements.txt

### Start Backend
uvicorn app.main:app --reload

### Start Streamlit
streamlit run app.py

### Place CSV files inside:
data/raw/

### Output
Cleaned CSV saved in data/cleaned/

Transformation summary displayed in UI
Full audit log available
Execution time displayed

## Design Principles

LLM used only for structured planning
Deterministic execution engine
Non-destructive data handling
Full transformation audit logging
Enterprise-safe guardrails

## Demo of the project

https://github.com/user-attachments/assets/a8163dcc-f4ec-4657-9826-c6f8dd3e2cb2



