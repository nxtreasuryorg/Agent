# Wallet Payment and Data Processing Tools

This module contains cryptocurrency wallet, payment functionality, Excel file processing, and Azure SQL Database operations extracted from the NxTreasury application for use with CrewAI agents.

## Features

### Wallet Payment Tools
- **Wallet Management**: Create new Ethereum wallets with encrypted private keys
- **Balance Checking**: Get ETH and USDT balances for any wallet address
- **Cryptocurrency Transfers**: Send ETH and USDT transactions
- **Transaction History**: Retrieve transaction history from Etherscan
- **Gas Estimation**: Calculate gas costs for transactions
- **Address Validation**: Validate Ethereum addresses

### Excel Reader Tools
- **File Reading**: Read Excel (.xlsx, .xls) and CSV files into pandas DataFrames
- **Data Analysis**: Analyze Excel data and extract insights
- **File Validation**: Validate Excel file structure against required columns
- **Data Conversion**: Convert Excel files to CSV format
- **Preview Generation**: Generate HTML previews of Excel data

### Azure SQL Database Tools
- **Database Connectivity**: Connect to Azure SQL Database with SQL authentication
- **Query Execution**: Execute SQL queries and return results as DataFrames
- **Table Operations**: Create, truncate, and manage database tables
- **Data Upload**: Upload pandas DataFrames to Azure SQL tables
- **Schema Management**: Check table existence and retrieve column information

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Wallet Payment Tools
export INFURA_API_KEY="your_infura_project_id"
export FERNET_KEY="your_fernet_encryption_key"
export ETHERSCAN_API_KEY="your_etherscan_api_key"  # Optional

# Azure SQL Database Tools
export AZURE_SQL_SERVER="your_server.database.windows.net"
export AZURE_SQL_DATABASE="your_database_name"
export AZURE_SQL_USERNAME="your_username"
export AZURE_SQL_PASSWORD="your_password"
```

## Environment Variables

### Required for Wallet Tools
- `INFURA_API_KEY`: Required for Ethereum blockchain connection
- `FERNET_KEY`: Required for private key encryption/decryption

### Required for Azure SQL Tools
- `AZURE_SQL_SERVER`: Azure SQL Server name
- `AZURE_SQL_DATABASE`: Database name
- `AZURE_SQL_USERNAME`: Database username
- `AZURE_SQL_PASSWORD`: Database password

### Optional
- `ETHERSCAN_API_KEY`: For transaction history features

## Usage Examples

### Wallet Operations

```python
from wallet_payment_tools import generate_new_wallet, check_wallet_balance

# Generate a new wallet
wallet_info = generate_new_wallet()
print(f"New wallet address: {wallet_info['public_address']}")

# Check wallet balance
balance_info = check_wallet_balance("0x742d35Cc6635C0532925a3b8D0f3e4B5C6e8F95", "both")
print(f"ETH Balance: {balance_info['eth_balance']}")
print(f"USDT Balance: {balance_info['usdt_balance']}")
```

### Excel File Processing

```python
from excel_azure_tools import ExcelReaderTools, read_excel_to_dataframe, analyze_excel_file

# Read Excel file using utility function
result = read_excel_to_dataframe("data.xlsx")
if result['success']:
    print(f"Loaded {result['rows']} rows with columns: {result['column_names']}")

# Analyze Excel file
analysis = analyze_excel_file("financial_data.xlsx")
if analysis['success']:
    print(f"Total amount: {analysis['total_amount']}")
    print(f"Currency breakdown: {analysis.get('currency_breakdown', 'N/A')}")

# Advanced usage with class
excel_tools = ExcelReaderTools()
df = excel_tools.read_excel_file("data.xlsx")
preview_html = excel_tools.get_file_preview("data.xlsx")
validation = excel_tools.validate_excel_structure("data.xlsx", ["Date", "Amount", "Currency"])
```

### Azure SQL Database Operations

```python
from excel_azure_tools import AzureSQLTools, query_azure_sql, excel_to_azure_sql

# Query database using utility function
result = query_azure_sql("SELECT TOP 10 * FROM sales_data")
if result['success']:
    print(f"Found {result['rows']} rows")
    for row in result['data']:
        print(row)

# Upload Excel data to database
upload_result = excel_to_azure_sql("sales_data.xlsx", "sales_table")
if upload_result['success']:
    print(f"Uploaded {upload_result['rows_inserted']} rows to {upload_result['table_name']}")

# Advanced usage with class
sql_tools = AzureSQLTools()
df = sql_tools.query_to_dataframe("SELECT * FROM customers WHERE country = ?", ("USA",))
table_info = sql_tools.get_table_columns("sales_data")
sql_tools.update_table_from_dataframe(df, "processed_data")
```

### Combined Excel and Database Workflow

```python
from excel_azure_tools import ExcelReaderTools, AzureSQLTools

# Read and process Excel file
excel_tools = ExcelReaderTools()
df = excel_tools.read_excel_file("monthly_report.xlsx")

# Analyze the data
analysis = excel_tools.analyze_excel_data("monthly_report.xlsx")
print(f"Processing {analysis['total_rows']} rows with total amount: {analysis['total_amount']}")

# Upload to Azure SQL Database
sql_tools = AzureSQLTools()
rows_inserted = sql_tools.update_table_from_dataframe(df, "monthly_reports")
print(f"Successfully uploaded {rows_inserted} rows to database")

# Query the uploaded data
results = sql_tools.query_to_dataframe("SELECT Currency, SUM(Amount) as Total FROM monthly_reports GROUP BY Currency")
print("Currency totals:")
print(results)
```

## CrewAI Integration

These tools are designed to work seamlessly with CrewAI agents. Each function returns structured data that can be easily processed by AI agents.

### Example CrewAI Tool Registration

```python
from crewai_tools import tool
from excel_azure_tools import read_excel_to_dataframe, analyze_excel_file, excel_to_azure_sql, query_azure_sql

@tool("Read Excel File")
def read_excel_tool(file_path: str, sheet_name: int = 0) -> dict:
    """Read an Excel file and return its data structure and sample data."""
    return read_excel_to_dataframe(file_path, sheet_name)

@tool("Analyze Excel Data")
def analyze_excel_tool(file_path: str) -> dict:
    """Analyze an Excel file and return statistical insights."""
    return analyze_excel_file(file_path)

@tool("Upload Excel to Database")
def upload_excel_tool(file_path: str, table_name: str) -> dict:
    """Upload Excel file data to Azure SQL Database."""
    return excel_to_azure_sql(file_path, table_name)

@tool("Query Database")
def query_db_tool(query: str, params: list = None) -> dict:
    """Execute a SQL query against Azure SQL Database."""
    return query_azure_sql(query, tuple(params) if params else None)
```

## System Requirements

### For Azure SQL Connectivity
- **ODBC Driver 18 for SQL Server** must be installed on your system
- **Windows**: Usually included with SQL Server installations
- **Linux**: Install via package manager (e.g., `apt-get install msodbcsql18`)
- **macOS**: Install via Homebrew (`brew tap microsoft/mssql-release && brew install msodbcsql18`)

### Python Version
- Python 3.8 or higher recommended
- pandas 2.0+ for optimal performance
- pyodbc 4.0+ for Azure SQL connectivity

## Security Considerations

### Wallet Tools
1. **Private Key Storage**: Private keys are encrypted using Fernet encryption
2. **Environment Variables**: Never commit API keys or encryption keys to version control
3. **Gas Limits**: Safety checks for gas limits and minimum balances included

### Database Tools
1. **Connection Security**: Uses encrypted connections to Azure SQL Database
2. **SQL Injection Protection**: Parameterized queries prevent SQL injection
3. **Credential Management**: Store database credentials securely in environment variables

## Error Handling

All functions include comprehensive error handling and return structured responses with success/failure status and descriptive error messages.

## Performance Considerations

- **Batch Processing**: Database operations use batching for large datasets
- **Memory Management**: Large Excel files are processed efficiently with pandas
- **Connection Pooling**: Database connections are properly managed and closed
- **Progress Tracking**: Long-running operations show progress indicators

## Supported File Formats

### Excel Tools
- **Excel**: .xlsx, .xls files
- **CSV**: .csv files with automatic delimiter detection
- **Sheet Selection**: Support for multiple sheets in Excel files

### Database Tools
- **Azure SQL Database**: Primary target database
- **SQL Server**: Compatible with on-premises SQL Server instances
- **Data Types**: Automatic mapping between pandas and SQL Server data types

## Contributing

This module is extracted from the NxTreasury application. For updates or modifications, refer to the main application repository. 