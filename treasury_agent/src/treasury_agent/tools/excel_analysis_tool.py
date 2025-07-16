from crewai.tools import BaseTool
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
import pandas as pd
import json
import os
from datetime import datetime
import re
from pathlib import Path


class ExcelAnalysisInput(BaseModel):
    """Input schema for ExcelAnalysisTool."""
    file_path: str = Field(..., description="Path to the Excel file to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis: 'comprehensive', 'payment_focused', 'financial_summary'")


class ExcelAnalysisTool(BaseTool):
    name: str = "Excel Analysis Tool"
    description: str = (
        "Analyze any Excel file dynamically and transform it into LLM-consumable format for payment decisions. "
        "This tool can handle any spreadsheet structure, extract all data, and provide both raw data and processed insights. "
        "Use this tool to process client financial data for payment analysis and decision-making."
    )
    args_schema: Type[BaseModel] = ExcelAnalysisInput

    def _run(self, file_path: str, analysis_type: str = "comprehensive") -> str:
        """
        Analyze Excel file and return comprehensive data in LLM-consumable format.
        
        Args:
            file_path: Path to the Excel file
            analysis_type: Type of analysis to perform
            
        Returns:
            JSON string containing complete Excel data and analysis
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return json.dumps({
                    "error": f"File not found: {file_path}",
                    "status": "error"
                }, indent=2)

            # Extract all data from Excel file
            excel_data = self._extract_excel_data(file_path)
            
            # Perform financial analysis
            financial_analysis = self._analyze_financial_data(excel_data)
            
            # Generate payment-focused insights
            payment_insights = self._generate_payment_insights(excel_data, financial_analysis)
            
            # Create comprehensive output
            result = self._create_comprehensive_output(
                file_path, excel_data, financial_analysis, payment_insights
            )
            
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({
                "error": f"Error analyzing Excel file: {str(e)}",
                "status": "error"
            }, indent=2)

    def _extract_excel_data(self, file_path: str) -> Dict[str, Any]:
        """Extract all data from Excel file, preserving complete structure."""
        excel_data = {
            "metadata": {},
            "sheets": {},
            "raw_data": {},
            "data_quality": {}
        }
        
        try:
            # Read Excel file with all sheets
            excel_file = pd.ExcelFile(file_path)
            
            # Extract metadata
            excel_data["metadata"] = {
                "file_name": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path),
                "sheets": excel_file.sheet_names,
                "processing_timestamp": datetime.now().isoformat(),
                "total_sheets": len(excel_file.sheet_names)
            }
            
            # Process each sheet
            for sheet_name in excel_file.sheet_names:
                try:
                    # Read sheet data
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                    
                    # Extract complete data
                    sheet_data = {
                        "headers": self._extract_headers(df),
                        "rows": self._extract_rows(df),
                        "data_types": self._analyze_data_types(df),
                        "missing_values": self._identify_missing_values(df),
                        "total_rows": len(df),
                        "total_columns": len(df.columns) if len(df.columns) > 0 else 0
                    }
                    
                    excel_data["sheets"][sheet_name] = sheet_data
                    excel_data["raw_data"][sheet_name] = df.to_dict('records')
                    
                except Exception as e:
                    excel_data["sheets"][sheet_name] = {
                        "error": f"Error processing sheet {sheet_name}: {str(e)}",
                        "total_rows": 0,
                        "total_columns": 0
                    }
            
            # Analyze data quality
            excel_data["data_quality"] = self._assess_data_quality(excel_data)
            
        except Exception as e:
            excel_data["error"] = f"Error reading Excel file: {str(e)}"
        
        return excel_data

    def _extract_headers(self, df: pd.DataFrame) -> List[str]:
        """Extract and clean column headers."""
        if len(df.columns) == 0:
            return []
        
        # Try to identify headers (first row with meaningful data)
        headers = []
        for col in df.columns:
            value = df.iloc[0, col] if len(df) > 0 else f"Column_{col}"
            if pd.isna(value):
                headers.append(f"Column_{col}")
            else:
                headers.append(str(value).strip())
        
        return headers

    def _extract_rows(self, df: pd.DataFrame) -> List[List[Any]]:
        """Extract all rows as lists, preserving all data."""
        rows = []
        for _, row in df.iterrows():
            row_data = []
            for value in row:
                if pd.isna(value):
                    row_data.append(None)
                else:
                    row_data.append(value)
            rows.append(row_data)
        return rows

    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Analyze data types in each column."""
        data_types = {}
        for col in df.columns:
            if len(df) == 0:
                data_types[f"Column_{col}"] = "empty"
                continue
                
            # Sample non-null values to determine type
            sample_values = df[col].dropna().head(10)
            if len(sample_values) == 0:
                data_types[f"Column_{col}"] = "empty"
            else:
                # Analyze sample values
                sample_str = str(sample_values.iloc[0])
                if self._is_currency(sample_str):
                    data_types[f"Column_{col}"] = "currency"
                elif self._is_date(sample_str):
                    data_types[f"Column_{col}"] = "date"
                elif self._is_numeric(sample_str):
                    data_types[f"Column_{col}"] = "numeric"
                else:
                    data_types[f"Column_{col}"] = "text"
        
        return data_types

    def _identify_missing_values(self, df: pd.DataFrame) -> Dict[str, int]:
        """Identify missing values in each column."""
        missing_values = {}
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_values[f"Column_{col}"] = int(missing_count)
        return missing_values

    def _assess_data_quality(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall data quality."""
        total_rows = sum(sheet.get("total_rows", 0) for sheet in excel_data["sheets"].values())
        total_columns = sum(sheet.get("total_columns", 0) for sheet in excel_data["sheets"].values())
        
        # Calculate confidence score based on data completeness
        total_cells = total_rows * total_columns if total_columns > 0 else 0
        missing_cells = sum(
            sum(sheet.get("missing_values", {}).values())
            for sheet in excel_data["sheets"].values()
        )
        
        confidence_score = 1.0 - (missing_cells / total_cells) if total_cells > 0 else 1.0
        
        return {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "confidence_score": round(confidence_score, 3),
            "data_completeness": f"{((total_cells - missing_cells) / total_cells * 100):.1f}%" if total_cells > 0 else "100%"
        }

    def _analyze_financial_data(self, excel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data patterns and extract insights."""
        financial_analysis = {
            "payment_data": {},
            "balance_data": {},
            "transaction_patterns": {},
            "risk_indicators": {},
            "key_insights": []
        }
        
        for sheet_name, sheet_data in excel_data["sheets"].items():
            if "error" in sheet_data:
                continue
                
            # Analyze each sheet for financial patterns
            sheet_analysis = self._analyze_sheet_for_financial_data(sheet_data, sheet_name)
            
            # Merge insights
            for key in financial_analysis:
                if key in sheet_analysis:
                    if isinstance(financial_analysis[key], dict):
                        financial_analysis[key].update(sheet_analysis[key])
                    elif isinstance(financial_analysis[key], list):
                        financial_analysis[key].extend(sheet_analysis[key])
        
        return financial_analysis

    def _analyze_sheet_for_financial_data(self, sheet_data: Dict[str, Any], sheet_name: str) -> Dict[str, Any]:
        """Analyze a single sheet for financial data patterns."""
        analysis = {
            "payment_data": {},
            "balance_data": {},
            "transaction_patterns": {},
            "risk_indicators": {},
            "key_insights": []
        }
        
        headers = sheet_data.get("headers", [])
        rows = sheet_data.get("rows", [])
        data_types = sheet_data.get("data_types", {})
        
        # Look for payment-related columns
        payment_columns = self._identify_payment_columns(headers, data_types)
        balance_columns = self._identify_balance_columns(headers, data_types)
        
        # Extract payment data
        if payment_columns:
            analysis["payment_data"] = self._extract_payment_data(rows, headers, payment_columns)
            analysis["key_insights"].append(f"Found payment data in sheet '{sheet_name}'")
        
        # Extract balance data
        if balance_columns:
            analysis["balance_data"] = self._extract_balance_data(rows, headers, balance_columns)
            analysis["key_insights"].append(f"Found balance data in sheet '{sheet_name}'")
        
        # Analyze transaction patterns
        if payment_columns or balance_columns:
            analysis["transaction_patterns"] = self._analyze_transaction_patterns(rows, headers, payment_columns, balance_columns)
        
        return analysis

    def _identify_payment_columns(self, headers: List[str], data_types: Dict[str, str]) -> List[str]:
        """Identify columns that likely contain payment data."""
        payment_keywords = [
            "payment", "amount", "transaction", "transfer", "send", "receive",
            "debit", "credit", "withdrawal", "deposit", "fee", "cost"
        ]
        
        payment_columns = []
        for header in headers:
            header_lower = header.lower()
            if any(keyword in header_lower for keyword in payment_keywords):
                payment_columns.append(header)
            elif data_types.get(header, "") == "currency":
                payment_columns.append(header)
        
        return payment_columns

    def _identify_balance_columns(self, headers: List[str], data_types: Dict[str, str]) -> List[str]:
        """Identify columns that likely contain balance data."""
        balance_keywords = [
            "balance", "account", "total", "sum", "available", "funds",
            "cash", "money", "assets", "equity"
        ]
        
        balance_columns = []
        for header in headers:
            header_lower = header.lower()
            if any(keyword in header_lower for keyword in balance_keywords):
                balance_columns.append(header)
            elif data_types.get(header, "") == "currency":
                balance_columns.append(header)
        
        return balance_columns

    def _extract_payment_data(self, rows: List[List[Any]], headers: List[str], payment_columns: List[str]) -> Dict[str, Any]:
        """Extract and analyze payment data."""
        payment_data = {
            "total_payments": 0,
            "total_amount": 0.0,
            "payment_list": [],
            "payment_summary": {}
        }
        
        for row in rows:
            if len(row) != len(headers):
                continue
                
            payment_record = {}
            has_payment_data = False
            
            for i, header in enumerate(headers):
                if header in payment_columns and i < len(row):
                    value = row[i]
                    if value is not None and self._is_numeric(str(value)):
                        payment_record[header] = value
                        has_payment_data = True
            
            if has_payment_data:
                payment_data["payment_list"].append(payment_record)
                payment_data["total_payments"] += 1
                
                # Sum payment amounts
                for col in payment_columns:
                    if col in payment_record:
                        try:
                            amount = float(payment_record[col])
                            payment_data["total_amount"] += amount
                        except (ValueError, TypeError):
                            pass
        
        return payment_data

    def _extract_balance_data(self, rows: List[List[Any]], headers: List[str], balance_columns: List[str]) -> Dict[str, Any]:
        """Extract and analyze balance data."""
        balance_data = {
            "current_balances": {},
            "total_balance": 0.0,
            "balance_summary": {}
        }
        
        # Get the most recent balance (last row with balance data)
        for row in reversed(rows):
            if len(row) != len(headers):
                continue
                
            for i, header in enumerate(headers):
                if header in balance_columns and i < len(row):
                    value = row[i]
                    if value is not None and self._is_numeric(str(value)):
                        try:
                            amount = float(value)
                            balance_data["current_balances"][header] = amount
                            balance_data["total_balance"] += amount
                        except (ValueError, TypeError):
                            pass
        
        return balance_data

    def _analyze_transaction_patterns(self, rows: List[List[Any]], headers: List[str], 
                                    payment_columns: List[str], balance_columns: List[str]) -> Dict[str, Any]:
        """Analyze transaction patterns for risk assessment."""
        patterns = {
            "frequency": "unknown",
            "amount_range": "unknown",
            "risk_level": "low",
            "patterns_detected": []
        }
        
        if not payment_columns:
            return patterns
        
        # Analyze payment frequency
        payment_count = len([row for row in rows if any(
            i < len(row) and headers[i] in payment_columns and 
            row[i] is not None and self._is_numeric(str(row[i]))
            for i in range(len(headers))
        )])
        
        if payment_count > 100:
            patterns["frequency"] = "high"
            patterns["risk_level"] = "medium"
        elif payment_count > 50:
            patterns["frequency"] = "medium"
        else:
            patterns["frequency"] = "low"
        
        return patterns

    def _generate_payment_insights(self, excel_data: Dict[str, Any], financial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate payment-focused insights for LLM consumption."""
        insights = {
            "available_funds": 0.0,
            "payment_obligations": [],
            "payment_history": [],
            "routing_preferences": {},
            "risk_factors": [],
            "recommendations": []
        }
        
        # Calculate available funds
        total_balance = financial_analysis.get("balance_data", {}).get("total_balance", 0.0)
        total_payments = financial_analysis.get("payment_data", {}).get("total_amount", 0.0)
        insights["available_funds"] = max(0.0, total_balance - total_payments)
        
        # Extract payment history
        payment_list = financial_analysis.get("payment_data", {}).get("payment_list", [])
        insights["payment_history"] = payment_list[:10]  # Last 10 payments
        
        # Generate risk factors
        patterns = financial_analysis.get("transaction_patterns", {})
        if patterns.get("frequency") == "high":
            insights["risk_factors"].append("High transaction frequency detected")
        if patterns.get("risk_level") == "medium":
            insights["risk_factors"].append("Medium risk transaction patterns")
        
        # Generate recommendations
        if insights["available_funds"] > 10000:
            insights["recommendations"].append("Sufficient funds available for payments")
        elif insights["available_funds"] > 0:
            insights["recommendations"].append("Limited funds available - prioritize payments")
        else:
            insights["recommendations"].append("Insufficient funds - review balance requirements")
        
        return insights

    def _create_comprehensive_output(self, file_path: str, excel_data: Dict[str, Any], 
                                   financial_analysis: Dict[str, Any], payment_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive output for LLM consumption."""
        return {
            "status": "success",
            "excel_metadata": excel_data["metadata"],
            "raw_data": excel_data["raw_data"],
            "processed_insights": {
                "financial_analysis": financial_analysis,
                "payment_analysis": payment_insights
            },
            "data_quality": excel_data["data_quality"],
            "llm_ready_summary": {
                "total_sheets": excel_data["metadata"]["total_sheets"],
                "total_rows": excel_data["data_quality"]["total_rows"],
                "available_funds": payment_insights["available_funds"],
                "payment_count": len(payment_insights["payment_history"]),
                "risk_level": "low" if not payment_insights["risk_factors"] else "medium",
                "key_insights": financial_analysis.get("key_insights", [])
            }
        }

    def _is_currency(self, value: str) -> bool:
        """Check if a value looks like currency."""
        currency_patterns = [
            r'^\$[\d,]+\.?\d*$',
            r'^€[\d,]+\.?\d*$',
            r'^£[\d,]+\.?\d*$',
            r'^[\d,]+\.?\d*\s*(USD|EUR|GBP|JPY)$'
        ]
        return any(re.match(pattern, str(value)) for pattern in currency_patterns)

    def _is_date(self, value: str) -> bool:
        """Check if a value looks like a date."""
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{2}/\d{2}/\d{4}$',
            r'^\d{2}-\d{2}-\d{4}$'
        ]
        return any(re.match(pattern, str(value)) for pattern in date_patterns)

    def _is_numeric(self, value: str) -> bool:
        """Check if a value is numeric."""
        try:
            # Remove currency symbols and commas
            cleaned_value = re.sub(r'[$,€£¥,\s]', '', str(value))
            float(cleaned_value)
            return True
        except (ValueError, TypeError):
            return False 