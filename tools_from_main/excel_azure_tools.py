"""
Excel Reader and Azure Database Tools - Extracted from NxTreasury Application
These tools provide Excel file reading and Azure SQL Database operations for CrewAI agents.
"""

import os
import pandas as pd
import numpy as np
import pyodbc
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from tqdm import tqdm
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv


class AzureSQLTools:
    """
    A comprehensive toolkit for Azure SQL Database operations.
    Handles connections, queries, table operations, and DataFrame integration.
    """
    
    def __init__(self, server=None, database=None, username=None, password=None, config_path=None):
        """
        Initialize Azure SQL connection.
        
        Args:
            server (str): SQL Server name
            database (str): Database name  
            username (str): Username
            password (str): Password
            config_path (str): Path to YAML config file (optional)
        """
        # Load from environment variables first
        self.server = server or os.getenv('AZURE_SQL_SERVER')
        self.database = database or os.getenv('AZURE_SQL_DATABASE')
        self.username = username or os.getenv('AZURE_SQL_USERNAME')
        self.password = password or os.getenv('AZURE_SQL_PASSWORD')
        
        # Fall back to config file if environment variables not available
        if not all([self.server, self.database, self.username, self.password]) and config_path:
            self._load_from_config(config_path)
        
        # Validate required parameters
        if not all([self.server, self.database, self.username, self.password]):
            raise ValueError("Azure SQL connection parameters must be provided via environment variables, parameters, or config file")
    
    def _load_from_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            self.server = self.server or config.get('SQL_SERVER')
            self.database = self.database or config.get('SQL_DATABASE')
            self.username = self.username or config.get('SQL_USERNAME')
            self.password = self.password or config.get('SQL_PASSWORD')
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    def get_connection(self):
        """
        Establish and return a connection to the Azure SQL Database.
        
        Returns:
            pyodbc.Connection: An open connection to the database
        """
        try:
            connection_string = (
                f"Driver={{ODBC Driver 18 for SQL Server}};"
                f"Server={self.server};"
                f"Database={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                "Encrypt=yes;TrustServerCertificate=no;"
            )
            
            connection = pyodbc.connect(connection_string)
            return connection
        
        except pyodbc.Error as e:
            raise Exception(f"Error connecting to Azure SQL Database: {e}")
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the results.
        
        Args:
            query (str): The SQL query to execute
            params (tuple, optional): Parameters for the query
            
        Returns:
            tuple: (columns, results) for SELECT queries, (None, row_count) for others
        """
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # If the query is a SELECT statement, fetch and return results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                return columns, results
            else:
                # For non-SELECT queries, commit the transaction and return affected row count
                connection.commit()
                return None, cursor.rowcount
        finally:
            connection.close()
    
    def query_to_dataframe(self, query, params=None):
        """
        Execute a SQL query and return the results as a pandas DataFrame.
        
        Args:
            query (str): The SQL query to execute
            params (tuple, optional): Parameters for the query
            
        Returns:
            pandas.DataFrame: A DataFrame containing the query results
        """
        columns, results = self.execute_query(query, params)
        if columns and results:
            return pd.DataFrame.from_records(results, columns=columns)
        return pd.DataFrame()
    
    def table_exists(self, table_name, schema='dbo'):
        """
        Check if a table exists in the database.
        
        Args:
            table_name (str): The name of the table to check
            schema (str): The database schema (default: 'dbo')
            
        Returns:
            bool: True if the table exists, False otherwise
        """
        query = """
        SELECT COUNT(1) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        """
        _, results = self.execute_query(query, (schema, table_name))
        return results[0][0] > 0
    
    def get_table_columns(self, table_name, schema='dbo'):
        """
        Get the column names for a table.
        
        Args:
            table_name (str): The name of the table
            schema (str): The database schema (default: 'dbo')
            
        Returns:
            list: A list of column names
        """
        query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        columns, results = self.execute_query(query, (schema, table_name))
        return [row[0] for row in results]
    
    def create_table_from_dataframe(self, df, table_name, schema='dbo'):
        """
        Create a new table based on a DataFrame's structure.
        
        Args:
            df (pandas.DataFrame): The DataFrame to use as a template
            table_name (str): The name of the table to create
            schema (str): The database schema (default: 'dbo')
            
        Returns:
            bool: True if the table was created successfully, False otherwise
        """
        if df.empty:
            print("DataFrame is empty, cannot create table.")
            return False
        
        # Map pandas dtypes to SQL Server data types
        dtype_map = {
            'int64': 'INT',
            'float64': 'FLOAT',
            'bool': 'BIT',
            'datetime64[ns]': 'DATETIME2',
            'object': 'NVARCHAR(MAX)',
            'category': 'NVARCHAR(MAX)'
        }
        
        # Create column definitions
        column_defs = []
        for col_name, dtype in df.dtypes.items():
            sql_type = dtype_map.get(str(dtype), 'NVARCHAR(MAX)')
            column_defs.append(f"[{col_name}] {sql_type}")
        
        # Create the table
        create_query = f"""
        CREATE TABLE [{schema}].[{table_name}] (
            {', '.join(column_defs)}
        )
        """
        
        try:
            _, rows_affected = self.execute_query(create_query)
            print(f"Created table {schema}.{table_name} with {len(column_defs)} columns")
            return True
        except Exception as e:
            print(f"Error creating table {schema}.{table_name}: {e}")
            return False
    
    def truncate_table(self, table_name, schema='dbo'):
        """
        Truncate a table (remove all rows).
        
        Args:
            table_name (str): The name of the table to truncate
            schema (str): The database schema (default: 'dbo')
            
        Returns:
            bool: True if the table was truncated successfully, False otherwise
        """
        try:
            _, rows_affected = self.execute_query(f"TRUNCATE TABLE [{schema}].[{table_name}]")
            print(f"Truncated table {schema}.{table_name}")
            return True
        except Exception as e:
            print(f"Error truncating table {schema}.{table_name}: {e}")
            return False
    
    def insert_dataframe(self, df, table_name, schema='dbo', batch_size=1000):
        """
        Insert a pandas DataFrame into an Azure SQL Database table.
        
        Args:
            df (pandas.DataFrame): The DataFrame to insert
            table_name (str): The name of the target table
            schema (str): The database schema (default: 'dbo')
            batch_size (int): Number of rows to insert in each batch (default: 1000)
            
        Returns:
            int: The total number of rows inserted
        """
        if df.empty:
            print("DataFrame is empty, nothing to insert.")
            return 0
        
        connection = self.get_connection()
        try:
            cursor = connection.cursor()
            
            # Get column names and create placeholders for the SQL query
            columns = df.columns.tolist()
            placeholders = ', '.join(['?' for _ in columns])
            column_str = ', '.join([f"[{col}]" for col in columns])
            
            # Prepare the insert query
            insert_query = f"INSERT INTO [{schema}].[{table_name}] ({column_str}) VALUES ({placeholders})"
            
            # Insert data in batches
            total_rows = 0
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                rows = [tuple(row) for row in batch.values]
                cursor.executemany(insert_query, rows)
                connection.commit()
                total_rows += len(batch)
            
            return total_rows
        
        except pyodbc.Error as e:
            connection.rollback()
            raise Exception(f"Error inserting data: {e}")
        finally:
            connection.close()
    
    def update_table_from_dataframe(self, df, table_name, schema='dbo'):
        """
        Update a table with data from a DataFrame. This will create the table if it doesn't exist,
        or truncate and reload if it does exist.
        
        Args:
            df (pandas.DataFrame): The DataFrame with new data
            table_name (str): The name of the target table
            schema (str): The database schema (default: 'dbo')
            
        Returns:
            int: The total number of rows inserted
        """
        # Check if table exists
        if not self.table_exists(table_name, schema):
            print(f"Table {schema}.{table_name} does not exist. Creating it.")
            self.create_table_from_dataframe(df, table_name, schema)
        else:
            print(f"Table {schema}.{table_name} exists. Truncating it.")
            self.truncate_table(table_name, schema)
        
        # Insert the data
        return self.insert_dataframe(df, table_name, schema)


class ExcelReaderTools:
    """
    A comprehensive toolkit for Excel file operations.
    Handles reading, processing, analysis, and data extraction from Excel files.
    """
    
    def __init__(self, upload_folder=None):
        """
        Initialize Excel reader tools.
        
        Args:
            upload_folder (str): Directory for file operations (optional)
        """
        if upload_folder:
            self.upload_folder = upload_folder
        else:
            # Default to a temporary folder
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.upload_folder = os.path.join(base_dir, 'temp_excel')
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def read_excel_file(self, file_path, sheet_name=0, skip_rows=0, clean_columns=True):
        """
        Read an Excel file into a pandas DataFrame.
        
        Args:
            file_path (str): Path to the Excel file
            sheet_name (int or str): Sheet to read (default: 0)
            skip_rows (int): Number of rows to skip (default: 0)
            clean_columns (bool): Whether to clean column names (default: True)
            
        Returns:
            pandas.DataFrame: The loaded DataFrame
        """
        try:
            # Determine file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
            elif file_ext == '.csv':
                df = pd.read_csv(file_path, skiprows=skip_rows)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            if clean_columns:
                # Clean column names
                df.columns = [
                    col.strip().replace(' ', '_').replace('.', '_').replace('-', '_') 
                    for col in df.columns
                ]
            
            # Basic data cleaning
            df = df.replace({pd.NA: None, pd.NaT: None})  # Replace pandas NA values with None
            df = df.dropna(how='all')  # Drop rows that are all NA
            
            print(f"Successfully loaded DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")
    
    def get_file_preview(self, file_path, rows=5):
        """
        Get a preview of an Excel file as HTML table.
        
        Args:
            file_path (str): Path to the Excel file
            rows (int): Number of rows to preview (default: 5)
            
        Returns:
            str: HTML table string
        """
        try:
            df = self.read_excel_file(file_path)
            preview = df.head(rows)
            
            # Format the table with styling
            html_table = preview.to_html(
                classes=['table', 'table-striped', 'table-bordered', 'table-hover', 'table-sm'],
                index=True,
                escape=False,
                float_format=lambda x: '{:.2f}'.format(x) if isinstance(x, float) else x
            )
            
            # Add custom styling
            styled_table = f"""
            <style>
                .table-sm td, .table-sm th {{
                    padding: 0.3rem;
                    font-size: 0.9rem;
                }}
                .table thead th {{
                    background-color: #f8f9fa;
                    border-bottom: 2px solid #dee2e6;
                }}
            </style>
            {html_table}
            """
            return styled_table
            
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def analyze_excel_data(self, file_path, currency_col='Currency', amount_col='Amount', date_col='Date'):
        """
        Analyze Excel data and extract insights.
        
        Args:
            file_path (str): Path to the Excel file
            currency_col (str): Name of currency column
            amount_col (str): Name of amount column
            date_col (str): Name of date column
            
        Returns:
            dict: Analysis results
        """
        try:
            df = self.read_excel_file(file_path, clean_columns=False)
            
            # Standardize column names (case-insensitive matching)
            col_mapping = {}
            for col in df.columns:
                col_lower = col.strip().lower()
                if col_lower in ['currency', 'curr', 'cur']:
                    col_mapping[col] = 'Currency'
                elif col_lower in ['amount', 'value', 'val', 'amt']:
                    col_mapping[col] = 'Amount'
                elif col_lower in ['date', 'datetime', 'time']:
                    col_mapping[col] = 'Date'
            
            df = df.rename(columns=col_mapping)
            
            # Check for required columns
            if 'Amount' not in df.columns:
                return {"error": "Amount column not found"}
            
            # Convert amounts to numeric
            df['Amount'] = pd.to_numeric(
                df['Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True), 
                errors='coerce'
            )
            
            # Basic analysis
            analysis = {
                'total_rows': len(df),
                'total_amount': float(df['Amount'].sum()),
                'average_amount': float(df['Amount'].mean()),
                'min_amount': float(df['Amount'].min()),
                'max_amount': float(df['Amount'].max()),
                'columns': df.columns.tolist(),
                'data_types': df.dtypes.to_dict()
            }
            
            # Currency analysis if Currency column exists
            if 'Currency' in df.columns:
                currency_summary = df.groupby('Currency')['Amount'].agg(['sum', 'count']).to_dict()
                analysis['currency_breakdown'] = currency_summary
            
            # Date analysis if Date column exists
            if 'Date' in df.columns:
                try:
                    df['Date'] = pd.to_datetime(df['Date'])
                    analysis['date_range'] = {
                        'start': df['Date'].min().isoformat() if pd.notna(df['Date'].min()) else None,
                        'end': df['Date'].max().isoformat() if pd.notna(df['Date'].max()) else None
                    }
                except:
                    analysis['date_range'] = None
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error analyzing file: {str(e)}"}
    
    def validate_excel_structure(self, file_path, required_columns=None):
        """
        Validate Excel file structure against required columns.
        
        Args:
            file_path (str): Path to the Excel file
            required_columns (list): List of required column names
            
        Returns:
            dict: Validation results
        """
        try:
            df = self.read_excel_file(file_path)
            
            validation = {
                'valid': True,
                'total_columns': len(df.columns),
                'total_rows': len(df),
                'columns_found': df.columns.tolist(),
                'missing_columns': [],
                'extra_columns': [],
                'empty_rows': 0,
                'issues': []
            }
            
            # Count empty rows
            validation['empty_rows'] = df.isnull().all(axis=1).sum()
            
            if required_columns:
                # Check for missing required columns (case-insensitive)
                df_columns_lower = [col.lower() for col in df.columns]
                required_lower = [col.lower() for col in required_columns]
                
                for req_col in required_columns:
                    if req_col.lower() not in df_columns_lower:
                        validation['missing_columns'].append(req_col)
                        validation['valid'] = False
                
                # Check for extra columns
                for col in df.columns:
                    if col.lower() not in required_lower:
                        validation['extra_columns'].append(col)
            
            # Check for data quality issues
            if df.empty:
                validation['issues'].append("File contains no data")
                validation['valid'] = False
            
            if validation['empty_rows'] > 0:
                validation['issues'].append(f"Found {validation['empty_rows']} empty rows")
            
            return validation
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Error validating file: {str(e)}"
            }
    
    def excel_to_csv(self, excel_path, csv_path=None, sheet_name=0):
        """
        Convert Excel file to CSV format.
        
        Args:
            excel_path (str): Path to the Excel file
            csv_path (str): Path for the output CSV file (optional)
            sheet_name (int or str): Sheet to convert
            
        Returns:
            str: Path to the created CSV file
        """
        try:
            if csv_path is None:
                # Generate CSV path based on Excel path
                base_name = os.path.splitext(excel_path)[0]
                csv_path = f"{base_name}.csv"
            
            df = self.read_excel_file(excel_path, sheet_name=sheet_name)
            df.to_csv(csv_path, index=False)
            
            print(f"Successfully converted {excel_path} to {csv_path}")
            return csv_path
            
        except Exception as e:
            raise Exception(f"Error converting Excel to CSV: {str(e)}")


# Utility functions for CrewAI tools
def create_azure_sql_instance():
    """
    Create an AzureSQLTools instance using environment variables.
    
    Returns:
        AzureSQLTools: Configured instance
    """
    return AzureSQLTools()


def create_excel_reader_instance():
    """
    Create an ExcelReaderTools instance.
    
    Returns:
        ExcelReaderTools: Configured instance
    """
    return ExcelReaderTools()


def read_excel_to_dataframe(file_path, sheet_name=0, skip_rows=0):
    """
    CrewAI tool: Read an Excel file and return data information.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (int or str): Sheet to read
        skip_rows (int): Number of rows to skip
        
    Returns:
        dict: File data and metadata
    """
    try:
        excel_tools = create_excel_reader_instance()
        df = excel_tools.read_excel_file(file_path, sheet_name, skip_rows)
        
        return {
            'success': True,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'data_sample': df.head().to_dict('records'),
            'data_types': df.dtypes.to_dict(),
            'message': f'Successfully read Excel file with {len(df)} rows and {len(df.columns)} columns'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def analyze_excel_file(file_path):
    """
    CrewAI tool: Analyze an Excel file and return insights.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        dict: Analysis results
    """
    try:
        excel_tools = create_excel_reader_instance()
        analysis = excel_tools.analyze_excel_data(file_path)
        
        if 'error' in analysis:
            return {
                'success': False,
                'error': analysis['error']
            }
        
        return {
            'success': True,
            **analysis
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def excel_to_azure_sql(file_path, table_name, server=None, database=None, username=None, password=None):
    """
    CrewAI tool: Upload Excel file data to Azure SQL Database.
    
    Args:
        file_path (str): Path to the Excel file
        table_name (str): Name of the target table
        server (str): SQL Server (optional if set in env)
        database (str): Database name (optional if set in env)
        username (str): Username (optional if set in env)
        password (str): Password (optional if set in env)
        
    Returns:
        dict: Upload results
    """
    try:
        # Read Excel file
        excel_tools = create_excel_reader_instance()
        df = excel_tools.read_excel_file(file_path)
        
        # Connect to Azure SQL
        sql_tools = AzureSQLTools(server, database, username, password)
        
        # Upload data
        rows_inserted = sql_tools.update_table_from_dataframe(df, table_name)
        
        return {
            'success': True,
            'table_name': table_name,
            'rows_inserted': rows_inserted,
            'columns': len(df.columns),
            'message': f'Successfully uploaded {rows_inserted} rows to table {table_name}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def query_azure_sql(query, params=None, return_dataframe=True):
    """
    CrewAI tool: Execute a query against Azure SQL Database.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters (optional)
        return_dataframe (bool): Whether to return as DataFrame (default: True)
        
    Returns:
        dict: Query results
    """
    try:
        sql_tools = create_azure_sql_instance()
        
        if return_dataframe:
            df = sql_tools.query_to_dataframe(query, params)
            return {
                'success': True,
                'rows': len(df),
                'columns': len(df.columns) if not df.empty else 0,
                'data': df.to_dict('records') if not df.empty else [],
                'column_names': df.columns.tolist() if not df.empty else []
            }
        else:
            columns, results = sql_tools.execute_query(query, params)
            return {
                'success': True,
                'columns': columns,
                'results': results,
                'row_count': len(results) if results else 0
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_azure_table_info(table_name, schema='dbo'):
    """
    CrewAI tool: Get information about a table in Azure SQL Database.
    
    Args:
        table_name (str): Name of the table
        schema (str): Database schema (default: 'dbo')
        
    Returns:
        dict: Table information
    """
    try:
        sql_tools = create_azure_sql_instance()
        
        if not sql_tools.table_exists(table_name, schema):
            return {
                'success': False,
                'error': f'Table {schema}.{table_name} does not exist'
            }
        
        columns = sql_tools.get_table_columns(table_name, schema)
        
        # Get row count
        count_query = f"SELECT COUNT(*) FROM [{schema}].[{table_name}]"
        _, results = sql_tools.execute_query(count_query)
        row_count = results[0][0] if results else 0
        
        return {
            'success': True,
            'table_name': table_name,
            'schema': schema,
            'columns': columns,
            'column_count': len(columns),
            'row_count': row_count,
            'exists': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        } 