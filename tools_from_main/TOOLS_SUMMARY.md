# Tools Summary - Extracted from NxTreasury

This document provides an overview of all tools extracted from the NxTreasury application for use with CrewAI agents.

## 📂 Tool Categories

### 1. Wallet Payment Tools (`wallet_payment_tools.py`)
**Source**: `nxtAppCore/utils.py`, `nxtAppCore/crypto.py`

**Key Functions**:
- `generate_new_wallet()` - Create new Ethereum wallets
- `check_wallet_balance()` - Check ETH and USDT balances
- `send_cryptocurrency()` - Send ETH/USDT transactions
- `get_gas_estimate()` - Estimate transaction costs

**Class**: `WalletPaymentTools`
- Wallet creation and management
- ETH and USDT balance checking
- Cryptocurrency transfers (ETH/USDT)
- Transaction history from Etherscan
- Gas price estimation
- Address validation
- Private key encryption/decryption

### 2. Excel Reader Tools (`excel_azure_tools.py`)
**Source**: `nxtAppCore/excel_handler.py`, `nxtAppCore/excel_to_sql_synchronizer.py`

**Key Functions**:
- `read_excel_to_dataframe()` - Read Excel files to DataFrames
- `analyze_excel_file()` - Analyze Excel data and extract insights

**Class**: `ExcelReaderTools`
- Read Excel (.xlsx, .xls) and CSV files
- Generate HTML previews of Excel data
- Validate Excel file structure
- Analyze Excel data for insights
- Convert Excel files to CSV format
- Data cleaning and preprocessing

### 3. Azure SQL Database Tools (`excel_azure_tools.py`)
**Source**: `nxtAppCore/azure_sql_connector.py`

**Key Functions**:
- `query_azure_sql()` - Execute SQL queries
- `excel_to_azure_sql()` - Upload Excel data to database
- `get_azure_table_info()` - Get table information

**Class**: `AzureSQLTools`
- Connect to Azure SQL Database
- Execute SQL queries and return DataFrames
- Create and manage database tables
- Upload pandas DataFrames to Azure SQL
- Table existence and schema checking
- Batch processing for large datasets

## 🔧 Environment Variables

### Required for Wallet Tools
```bash
INFURA_API_KEY=your_infura_project_id
FERNET_KEY=your_fernet_encryption_key
```

### Required for Azure SQL Tools
```bash
AZURE_SQL_SERVER=your_server.database.windows.net
AZURE_SQL_DATABASE=your_database_name
AZURE_SQL_USERNAME=your_username
AZURE_SQL_PASSWORD=your_password
```

### Optional
```bash
ETHERSCAN_API_KEY=your_etherscan_api_key  # For transaction history
```

## 📁 File Structure

```
tools/
├── __init__.py                    # Package initialization
├── wallet_payment_tools.py       # Wallet and payment functionality
├── excel_azure_tools.py          # Excel reader and Azure SQL tools
├── requirements.txt               # All dependencies
├── README.md                      # Comprehensive documentation
├── example_usage.py              # Complete usage examples
├── env_example.txt               # Environment variables template
└── TOOLS_SUMMARY.md              # This summary document
```

## 🚀 Quick Start Examples

### Wallet Operations
```python
from wallet_payment_tools import generate_new_wallet, check_wallet_balance

# Create new wallet
wallet = generate_new_wallet()
print(f"Address: {wallet['public_address']}")

# Check balance
balance = check_wallet_balance("0x742d35Cc6635C0532925a3b8D0f3e4B5C6e8F95")
print(f"ETH: {balance['eth_balance']}, USDT: {balance['usdt_balance']}")
```

### Excel Processing
```python
from excel_azure_tools import read_excel_to_dataframe, analyze_excel_file

# Read Excel file
data = read_excel_to_dataframe("data.xlsx")
print(f"Loaded {data['rows']} rows")

# Analyze Excel data
analysis = analyze_excel_file("financial_data.xlsx")
print(f"Total amount: {analysis['total_amount']}")
```

### Database Operations
```python
from excel_azure_tools import query_azure_sql, excel_to_azure_sql

# Query database
results = query_azure_sql("SELECT * FROM sales_data")
print(f"Found {results['rows']} rows")

# Upload Excel to database
upload = excel_to_azure_sql("data.xlsx", "new_table")
print(f"Uploaded {upload['rows_inserted']} rows")
```

## 🤖 CrewAI Integration

All tools are designed for CrewAI with:
- Structured return formats (success/error dictionaries)
- Comprehensive error handling
- Ready-to-use utility functions
- Easy tool registration

### Example Tool Registration
```python
from crewai_tools import tool
from excel_azure_tools import read_excel_to_dataframe

@tool("Read Excel File")
def read_excel_tool(file_path: str) -> dict:
    """Read an Excel file and return its structure."""
    return read_excel_to_dataframe(file_path)
```

## 📊 Capabilities Matrix

| Feature | Wallet Tools | Excel Tools | Azure SQL Tools |
|---------|-------------|-------------|-----------------|
| **Data Reading** | Blockchain data | Excel/CSV files | SQL Database |
| **Data Writing** | Transactions | CSV conversion | Table creation |
| **Analysis** | Balance/Gas | Statistical insights | Query results |
| **Validation** | Address validation | File structure | Schema checking |
| **Security** | Encrypted keys | File validation | Parameterized queries |
| **Batch Operations** | Multiple transfers | Large file processing | Bulk inserts |

## 🔄 Common Workflows

### 1. Excel → Database Pipeline
```python
# Read Excel → Analyze → Upload to Azure SQL
excel_data = read_excel_to_dataframe("report.xlsx")
analysis = analyze_excel_file("report.xlsx")  
upload_result = excel_to_azure_sql("report.xlsx", "monthly_reports")
```

### 2. Database → Analysis → Crypto
```python
# Query data → Analyze → Execute payments
data = query_azure_sql("SELECT * FROM pending_payments")
# Process payment logic
payment_result = send_cryptocurrency(encrypted_key, address, amount, "usdt")
```

### 3. Combined Financial Workflow
```python
# Excel analysis → Database storage → Crypto transactions
analysis = analyze_excel_file("treasury_report.xlsx")
excel_to_azure_sql("treasury_report.xlsx", "treasury_data")
balance_check = check_wallet_balance(treasury_wallet)
gas_estimate = get_gas_estimate("usdt")
```

## 🛠️ System Requirements

### Python Dependencies
- Python 3.8+
- pandas 2.0+
- web3 6.0+
- pyodbc 4.0+
- cryptography 3.4+

### System Dependencies
- **ODBC Driver 18 for SQL Server** (for Azure SQL connectivity)
- **Node.js/npm** (not required, but useful for some crypto operations)

### Database Support
- Azure SQL Database (primary)
- SQL Server (compatible)
- Automatic data type mapping

### Blockchain Support
- Ethereum Mainnet
- ETH and USDT transactions
- Infura node connectivity

## 🔒 Security Features

### Wallet Tools
- Fernet encryption for private keys
- Address validation
- Gas limit safety checks
- Secure random wallet generation

### Database Tools
- Encrypted connections
- Parameterized queries (SQL injection protection)
- Secure credential management
- Connection pooling

### Excel Tools
- File type validation
- Data sanitization
- Safe column name cleaning
- Memory-efficient processing

## 📈 Performance Characteristics

### Wallet Tools
- Real-time blockchain connectivity
- Gas price optimization
- Transaction batching support
- Efficient balance checking

### Excel Tools
- Large file support (100K+ rows)
- Memory-efficient reading
- Progress tracking for long operations
- Multiple sheet support

### Database Tools
- Batch insert operations (1000 rows/batch)
- Connection pooling
- Efficient DataFrame operations
- Large dataset handling

## 🔍 Error Handling

All tools include:
- Comprehensive exception handling
- Structured error responses
- Descriptive error messages
- Graceful failure modes
- Logging capabilities

## 📋 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set environment variables**: Copy `env_example.txt` to `.env`
3. **Test connectivity**: Run `python example_usage.py`
4. **Integrate with CrewAI**: Register tools with your agents
5. **Customize workflows**: Adapt functions for your specific use cases

---

**Extracted from**: NxTreasury Application  
**Target Use**: CrewAI Agents  
**Last Updated**: Current extraction  
**Status**: Ready for production use 