"""
Example usage of Wallet Payment Tools, Excel Reader Tools, and Azure SQL Tools
This file demonstrates how to use the extracted functionality.
"""

import os
from dotenv import load_dotenv
from wallet_payment_tools import (
    WalletPaymentTools,
    generate_new_wallet,
    check_wallet_balance,
    send_cryptocurrency,
    get_gas_estimate
)
from excel_azure_tools import (
    ExcelReaderTools,
    AzureSQLTools,
    read_excel_to_dataframe,
    analyze_excel_file,
    excel_to_azure_sql,
    query_azure_sql,
    get_azure_table_info
)

# Load environment variables from .env file
load_dotenv()

def example_basic_wallet_operations():
    """Example of basic wallet operations using the utility functions."""
    print("=== Basic Wallet Operations ===")
    
    # Generate a new wallet
    print("1. Generating a new wallet...")
    try:
        wallet_info = generate_new_wallet()
        if wallet_info['success']:
            print(f"   ✓ New wallet created: {wallet_info['public_address']}")
            print(f"   ✓ Private key encrypted and stored securely")
        else:
            print(f"   ✗ Failed to create wallet")
            return
    except Exception as e:
        print(f"   ✗ Error creating wallet: {str(e)}")
        return
    
    # Check balance of a sample address (Ethereum Foundation)
    sample_address = "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"
    print(f"\n2. Checking balance for address: {sample_address}")
    
    try:
        balance_info = check_wallet_balance(sample_address, "both")
        if balance_info['success']:
            print(f"   ✓ ETH Balance: {balance_info.get('eth_balance', 'N/A')} ETH")
            if balance_info.get('eth_usd_value'):
                print(f"   ✓ ETH USD Value: ${balance_info['eth_usd_value']:.2f}")
            print(f"   ✓ USDT Balance: {balance_info.get('usdt_balance', 'N/A')} USDT")
        else:
            print(f"   ✗ Error: {balance_info['error']}")
    except Exception as e:
        print(f"   ✗ Error checking balance: {str(e)}")

def example_excel_operations():
    """Example of Excel file operations."""
    print("\n=== Excel File Operations ===")
    
    # Create a sample Excel file for demonstration
    sample_file = "sample_data.xlsx"
    create_sample_excel_file(sample_file)
    
    try:
        # Read Excel file using utility function
        print("1. Reading Excel file...")
        result = read_excel_to_dataframe(sample_file)
        if result['success']:
            print(f"   ✓ Loaded {result['rows']} rows with {result['columns']} columns")
            print(f"   ✓ Columns: {result['column_names']}")
            print(f"   ✓ Sample data: {result['data_sample'][0] if result['data_sample'] else 'No data'}")
        else:
            print(f"   ✗ Error: {result['error']}")
            return
        
        # Analyze Excel file
        print("\n2. Analyzing Excel file...")
        analysis = analyze_excel_file(sample_file)
        if analysis['success']:
            print(f"   ✓ Total rows: {analysis['total_rows']}")
            print(f"   ✓ Total amount: {analysis['total_amount']:.2f}")
            print(f"   ✓ Average amount: {analysis['average_amount']:.2f}")
            if 'currency_breakdown' in analysis:
                print(f"   ✓ Currency breakdown available")
        else:
            print(f"   ✗ Error: {analysis['error']}")
        
        # Advanced operations with class
        print("\n3. Advanced Excel operations...")
        excel_tools = ExcelReaderTools()
        
        # Get file preview
        preview_html = excel_tools.get_file_preview(sample_file, rows=3)
        print("   ✓ Generated HTML preview")
        
        # Validate file structure
        required_columns = ['Date', 'Amount', 'Currency']
        validation = excel_tools.validate_excel_structure(sample_file, required_columns)
        if validation['valid']:
            print("   ✓ File structure validation passed")
        else:
            print(f"   ⚠ Validation issues: {validation.get('issues', [])}")
            print(f"   ⚠ Missing columns: {validation.get('missing_columns', [])}")
        
        # Convert to CSV
        csv_file = excel_tools.excel_to_csv(sample_file)
        print(f"   ✓ Converted to CSV: {csv_file}")
        
    except Exception as e:
        print(f"   ✗ Error in Excel operations: {str(e)}")
    finally:
        # Clean up sample files
        for file in [sample_file, "sample_data.csv"]:
            if os.path.exists(file):
                os.remove(file)

def example_azure_sql_operations():
    """Example of Azure SQL Database operations."""
    print("\n=== Azure SQL Database Operations ===")
    
    # Check if Azure SQL credentials are available
    required_vars = ['AZURE_SQL_SERVER', 'AZURE_SQL_DATABASE', 'AZURE_SQL_USERNAME', 'AZURE_SQL_PASSWORD']
    if not all(os.getenv(var) for var in required_vars):
        print("   ⚠ Azure SQL credentials not found, skipping database examples")
        print("   ⚠ Required environment variables:")
        for var in required_vars:
            status = "✓ Set" if os.getenv(var) else "✗ Not set"
            print(f"     {var}: {status}")
        return
    
    try:
        # Test connection
        print("1. Testing Azure SQL connection...")
        sql_tools = AzureSQLTools()
        connection = sql_tools.get_connection()
        connection.close()
        print("   ✓ Successfully connected to Azure SQL Database")
        
        # Create sample table and data
        print("\n2. Creating sample table...")
        sample_data = create_sample_dataframe()
        table_name = "sample_test_table"
        
        # Check if table exists and get info
        table_info = get_azure_table_info(table_name)
        if table_info['success'] and table_info['exists']:
            print(f"   ✓ Table {table_name} already exists with {table_info['row_count']} rows")
        else:
            print(f"   ✓ Table {table_name} does not exist, will create")
        
        # Upload data to database
        rows_inserted = sql_tools.update_table_from_dataframe(sample_data, table_name)
        print(f"   ✓ Uploaded {rows_inserted} rows to table {table_name}")
        
        # Query the data back
        print("\n3. Querying data from database...")
        query_result = query_azure_sql(f"SELECT TOP 5 * FROM {table_name}")
        if query_result['success']:
            print(f"   ✓ Retrieved {query_result['rows']} rows")
            print(f"   ✓ Columns: {query_result['column_names']}")
            if query_result['data']:
                print(f"   ✓ First row: {query_result['data'][0]}")
        
        # Get table information
        print("\n4. Getting table information...")
        table_info = get_azure_table_info(table_name)
        if table_info['success']:
            print(f"   ✓ Table: {table_info['table_name']}")
            print(f"   ✓ Columns: {table_info['columns']}")
            print(f"   ✓ Row count: {table_info['row_count']}")
        
        # Advanced query with parameters
        print("\n5. Executing parameterized query...")
        param_query = f"SELECT * FROM {table_name} WHERE Amount > ?"
        param_result = query_azure_sql(param_query, (100,))
        if param_result['success']:
            print(f"   ✓ Found {param_result['rows']} rows with amount > 100")
        
        # Clean up - drop the test table
        print("\n6. Cleaning up test table...")
        cleanup_result = query_azure_sql(f"DROP TABLE IF EXISTS {table_name}", return_dataframe=False)
        if cleanup_result['success']:
            print("   ✓ Test table cleaned up")
        
    except Exception as e:
        print(f"   ✗ Error in Azure SQL operations: {str(e)}")

def example_combined_workflow():
    """Example of combined Excel and database workflow."""
    print("\n=== Combined Excel + Database Workflow ===")
    
    # Check if both Excel tools and Azure SQL are available
    if not all(os.getenv(var) for var in ['AZURE_SQL_SERVER', 'AZURE_SQL_DATABASE', 'AZURE_SQL_USERNAME', 'AZURE_SQL_PASSWORD']):
        print("   ⚠ Azure SQL credentials not available, skipping combined workflow")
        return
    
    try:
        # Create sample Excel file
        excel_file = "workflow_sample.xlsx"
        create_sample_excel_file(excel_file)
        table_name = "excel_upload_test"
        
        print("1. Processing Excel file and uploading to database...")
        
        # Upload Excel data directly to database
        upload_result = excel_to_azure_sql(excel_file, table_name)
        if upload_result['success']:
            print(f"   ✓ Uploaded {upload_result['rows_inserted']} rows to {upload_result['table_name']}")
        else:
            print(f"   ✗ Upload failed: {upload_result['error']}")
            return
        
        # Analyze the uploaded data
        print("\n2. Analyzing uploaded data...")
        analysis_query = f"""
        SELECT 
            Currency,
            COUNT(*) as transaction_count,
            SUM(Amount) as total_amount,
            AVG(Amount) as avg_amount,
            MIN(Amount) as min_amount,
            MAX(Amount) as max_amount
        FROM {table_name}
        GROUP BY Currency
        ORDER BY total_amount DESC
        """
        
        analysis_result = query_azure_sql(analysis_query)
        if analysis_result['success']:
            print(f"   ✓ Currency analysis completed:")
            for row in analysis_result['data']:
                print(f"     {row['Currency']}: {row['transaction_count']} transactions, "
                      f"Total: {row['total_amount']:.2f}, Avg: {row['avg_amount']:.2f}")
        
        # Generate summary report
        print("\n3. Generating summary report...")
        summary_query = f"""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT Currency) as currency_count,
            SUM(Amount) as grand_total,
            MIN(Date) as earliest_date,
            MAX(Date) as latest_date
        FROM {table_name}
        """
        
        summary_result = query_azure_sql(summary_query)
        if summary_result['success'] and summary_result['data']:
            summary = summary_result['data'][0]
            print(f"   ✓ Total transactions: {summary['total_transactions']}")
            print(f"   ✓ Currencies: {summary['currency_count']}")
            print(f"   ✓ Grand total: {summary['grand_total']:.2f}")
            print(f"   ✓ Date range: {summary['earliest_date']} to {summary['latest_date']}")
        
        # Clean up
        print("\n4. Cleaning up...")
        cleanup_result = query_azure_sql(f"DROP TABLE IF EXISTS {table_name}", return_dataframe=False)
        if cleanup_result['success']:
            print("   ✓ Database table cleaned up")
        
        if os.path.exists(excel_file):
            os.remove(excel_file)
            print("   ✓ Excel file cleaned up")
        
    except Exception as e:
        print(f"   ✗ Error in combined workflow: {str(e)}")

def create_sample_excel_file(filename):
    """Create a sample Excel file for testing."""
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Generate sample data
    dates = [datetime.now() - timedelta(days=i) for i in range(10)]
    currencies = ['USD', 'EUR', 'BTC', 'ETH', 'USDT'] * 2
    amounts = [100.50, 250.75, 0.001, 0.5, 150.00, 300.25, 0.002, 1.2, 200.00, 450.80]
    types = ['Credit', 'Debit'] * 5
    
    data = {
        'Date': dates,
        'Currency': currencies,
        'Amount': amounts,
        'Type': types,
        'Description': [f'Transaction {i+1}' for i in range(10)]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

def create_sample_dataframe():
    """Create a sample DataFrame for database testing."""
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = [datetime.now() - timedelta(days=i) for i in range(5)]
    data = {
        'Date': dates,
        'Currency': ['USD', 'EUR', 'BTC', 'ETH', 'USDT'],
        'Amount': [100.00, 85.50, 50000.00, 3500.00, 99.99],
        'Type': ['Credit', 'Credit', 'Credit', 'Credit', 'Credit'],
        'Description': ['Sample transaction 1', 'Sample transaction 2', 'Sample transaction 3', 
                       'Sample transaction 4', 'Sample transaction 5']
    }
    
    return pd.DataFrame(data)

def example_gas_estimation():
    """Example of gas price estimation."""
    print("\n=== Gas Price Estimation ===")
    
    try:
        # Get gas estimate for ETH transaction
        eth_estimate = get_gas_estimate("eth")
        if eth_estimate['success']:
            print(f"ETH Transaction:")
            print(f"   Gas Limit: {eth_estimate['gas_limit']}")
            print(f"   Gas Price: {eth_estimate['gas_price_gwei']:.2f} Gwei")
            print(f"   Estimated Cost: {eth_estimate['estimated_cost_eth']:.6f} ETH")
        
        # Get gas estimate for USDT transaction
        usdt_estimate = get_gas_estimate("usdt")
        if usdt_estimate['success']:
            print(f"\nUSDT Transaction:")
            print(f"   Gas Limit: {usdt_estimate['gas_limit']}")
            print(f"   Gas Price: {usdt_estimate['gas_price_gwei']:.2f} Gwei")
            print(f"   Estimated Cost: {usdt_estimate['estimated_cost_eth']:.6f} ETH")
            
    except Exception as e:
        print(f"   ✗ Error getting gas estimates: {str(e)}")

def example_environment_check():
    """Check if required environment variables are set."""
    print("=== Environment Check ===")
    
    # Wallet tools variables
    wallet_vars = ['INFURA_API_KEY', 'FERNET_KEY']
    print("Wallet Tools environment variables:")
    for var in wallet_vars:
        value = os.getenv(var)
        status = "✓ Set" if value else "✗ Not set"
        print(f"   {var}: {status}")
    
    # Azure SQL variables
    azure_vars = ['AZURE_SQL_SERVER', 'AZURE_SQL_DATABASE', 'AZURE_SQL_USERNAME', 'AZURE_SQL_PASSWORD']
    print("\nAzure SQL environment variables:")
    for var in azure_vars:
        value = os.getenv(var)
        status = "✓ Set" if value else "✗ Not set"
        print(f"   {var}: {status}")
    
    # Optional variables
    optional_vars = ['ETHERSCAN_API_KEY']
    print("\nOptional environment variables:")
    for var in optional_vars:
        value = os.getenv(var)
        status = "✓ Set" if value else "- Not set"
        print(f"   {var}: {status}")

def main():
    """Run all examples."""
    print("Wallet Payment, Excel Reader, and Azure SQL Tools - Example Usage")
    print("=" * 80)
    
    # Check environment first
    example_environment_check()
    
    # Check if required variables are set for wallet operations
    wallet_ready = all(os.getenv(var) for var in ['INFURA_API_KEY', 'FERNET_KEY'])
    azure_ready = all(os.getenv(var) for var in ['AZURE_SQL_SERVER', 'AZURE_SQL_DATABASE', 'AZURE_SQL_USERNAME', 'AZURE_SQL_PASSWORD'])
    
    if not wallet_ready:
        print("\n⚠ Wallet tools environment variables not set.")
        print("Please set INFURA_API_KEY and FERNET_KEY before running wallet examples.")
    
    if not azure_ready:
        print("\n⚠ Azure SQL environment variables not set.")
        print("Please set Azure SQL connection variables before running database examples.")
    
    # Run examples based on available credentials
    try:
        if wallet_ready:
            example_basic_wallet_operations()
            example_gas_estimation()
        
        # Excel operations don't require special credentials
        example_excel_operations()
        
        if azure_ready:
            example_azure_sql_operations()
            example_combined_workflow()
        
        print("\n" + "=" * 80)
        print("All available examples completed!")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {str(e)}")

if __name__ == "__main__":
    main() 