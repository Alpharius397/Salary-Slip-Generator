# Salary Slip Generator

A Python-based GUI tool to automate the generation of salary slips for employees. The system supports bulk processing from structured input data and produces professional salary slip outputs in PDF format using wthmltopdf.

## Features
- Generate salary slips from Excel/CSV data  
- Dynamic PDF creation with employee-specific details  
- Configurable deductions, allowances, and salary structure  
- Supports bulk processing of large datasets  
- Supports bulk emailing of salary slips to all employees
- Securely store all data into local MySql database
- Optional conversion into executable for non-Python users  

## Requirements
Install dependencies:

```bash
pip install -r requirement.txt
```

## Executable Build
Build a exe using the following command

```bash
pyinstaller --onefile main/App.py
```

## Benchmarks

### Base Python Version
79 PDFs in 26s

### Async Python Version
798 PDFs in 29s
