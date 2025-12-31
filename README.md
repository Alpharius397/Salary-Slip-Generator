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

## Quickstart Guide

Just run the following command (Windows Only) to setup and compile the exe
```bash
build_exe
```

## Requirements
Install dependencies:

```bash
pip install -r requirement.txt
```

### Compile SqlCipher using pysqlite (works on my machine and needs Visual Studio)

0) Install OpenSSL v3.3.5 and TCL
Tcl is required to build SQLite. You can download it from [IronTCL](https://www.irontcl.com/). Once you have downloaded it, extract it to a folder and navigate to the bin directory. Copy the file tclsh86t.exe to tclsh.exe. This is because the build looks for tclsh.exe.


1) Clone the sqlcipher repo and switch to the v4.5.7 (Sqlite v3.45.3)
```bash
git clone https://github.com/sqlcipher/sqlcipher.git
git checkout v4.5.7
```


2) Follow this [guide](https://www.domstamand.com/compiling-sqlcipher-sqlite-encrypted-for-windows-using-visual-studio-2022/). Make sure to add this flags to the **Makefile.msc** at the appropriate place

```Makefile
TCC = $(TCC) -DSQLITE_HAS_CODEC -I"path\to\OpenSSL\include" -DSQLITE_TEMP_STORE=2 -MT

LTLIBPATHS = $(LTLIBPATHS) /LIBPATH:$(ICULIBDIR) /LIBPATH:"path\to\OpenSSL\libs\MT" # Ensure libcrypto and libssl exist here
LTLIBS = $(LTLIBS) libcrypto_static.lib libssl_static.lib ws2_32.lib shell32.lib advapi32.lib gdi32.lib user32.lib crypt32.lib kernel32.lib # Ensure to add only static.lib

# Pass libs to this to generate a completely linked .lib
libsqlite3.lib:	$(LIBOBJ)
	$(LTLIB) $(LTLIBOPTS) $(LTLIBPATHS) /OUT:$@ $(LIBOBJ) $(TLIBS) $(LTLIBS)

``` 

To build the lib open a command prompt using **x64 Native Tools Command Prompt for VS 2022** and run the following commands
```bash
SET PATH=%PATH%;\path\to\Tcl\bin

SET PLATFORM=x64

nmake /f <repo-root>\Makefile.msc TOP=<repo-root> libsqlite3.lib
```

For verification, run this command
```bash
dumpbin /symbols libsqlite3.lib | findstr HMAC_CTX
```

Ensure that atleast HMAC_CTX_* is not UNDEF (atleast one)


3) Now, simply copy the generated **libsqlite3.lib** to the installed python's lib folder (Should be like _Python\Python312\libs_) and rename it to **sqlite3.lib**

4) Also add the **sqlite3.h** from sqlcipher to the installed python's include folder (Should be like _Python\Python312\include_)

5) Last step, run this command to build the pysqlite3 wheel against sqlcipher's sqlite

```bash
pip install --no-binary pysqlite3 pysqlite3
```

If it succeeds, you can use it has following in the code
```python
import sys
import pysqlite3

sys.modules['sqlite3'] = pysqlite3

import sqlite3 # This will generate an encrypted sqlite db
```

**_NOTE: There is a pre-compiled sqlite3.lib and sqlite3.h in the main/bin folder_**

### wkhtmltopdf dependency
Install wkhtmltopdf and place the wkhtmltopdf.exe into the main/bin folder

### Creds addition

In the main folder, add the following file: **creds.py** with following code

```python
"Private Creds"
from dataType import SMTP_CRED

PROD_CREDS = SMTP_CRED(email="smtp-email", key="smtp-key") # Prod creds
TEST_CREDS = SMTP_CRED(email="smtp-email", key="smtp-key") # Test Creds 
```

## Executable Build
Build a exe using the following command

```bash
pyinstaller --onefile main/App.py --add-binary "main/bin/wkhtmltopdf.exe;./bin" --add-data "main/doc;./doc"
```

## Benchmarks

### Base Python Version
79 PDFs in 26s

### Async Python Version
798 PDFs in 29s
