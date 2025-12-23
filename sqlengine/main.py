# -*- coding: utf-8 -*-
# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Employee Database SQL Executor",
    description="SQL Executor API for employees database",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "employees"),
}

# 请求模型
class SQLQuery(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    params: Optional[List[Any]] = Field(default=None, description="Query parameters")

class SQLResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    rows_affected: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None

# 数据库连接依赖
def get_db_connection():
    """Get database connection"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        yield connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    finally:
        if connection and connection.is_connected():
            connection.close()

# SQL 安全检查
def is_safe_query(query: str) -> tuple:
    """Check if SQL query is safe"""
    query_upper = query.upper().strip()

    # Dangerous operations list
    dangerous_keywords = [
        "DROP DATABASE",
        "DROP TABLE",
        "TRUNCATE",
        "DELETE FROM employees",
        "DELETE FROM departments",
        "UPDATE employees SET",
        "UPDATE departments SET",
    ]

    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"Operation containing '{keyword}' is forbidden"

    return True, ""

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Employee Database SQL Executor API",
        "version": "1.0.0",
        "endpoints": {
            "execute": "/api/execute",
            "tables": "/api/tables",
            "table_info": "/api/table/{table_name}",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check(connection=Depends(get_db_connection)):
    """Health check endpoint"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection error: {str(e)}")

@app.post("/api/execute", response_model=SQLResponse)
async def execute_query(
    sql_query: SQLQuery,
    connection=Depends(get_db_connection)
):
    """Execute SQL query"""
    try:
        # Safety check
        is_safe, error_msg = is_safe_query(sql_query.query)
        if not is_safe:
            return SQLResponse(
                success=False,
                error=error_msg
            )

        cursor = connection.cursor(dictionary=True)

        # Execute query
        if sql_query.params:
            cursor.execute(sql_query.query, sql_query.params)
        else:
            cursor.execute(sql_query.query)

        # Check if it's a SELECT query
        if sql_query.query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            columns = cursor.column_names if cursor.column_names else []

            cursor.close()

            return SQLResponse(
                success=True,
                data=results,
                columns=list(columns),
                message=f"Query successful, returned {len(results)} records"
            )
        else:
            # Non-SELECT queries (INSERT, UPDATE, DELETE)
            connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            return SQLResponse(
                success=True,
                rows_affected=rows_affected,
                message=f"Operation successful, affected {rows_affected} rows"
            )

    except Error as e:
        logger.error(f"SQL execution error: {e}")
        return SQLResponse(
            success=False,
            error=f"SQL execution error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        return SQLResponse(
            success=False,
            error=f"Server error: {str(e)}"
        )

@app.get("/api/tables")
async def get_tables(connection=Depends(get_db_connection)):
    """Get all table names"""
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()

        return {
            "success": True,
            "tables": tables,
            "count": len(tables)
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table list: {str(e)}")

@app.get("/api/table/{table_name}")
async def get_table_info(table_name: str, connection=Depends(get_db_connection)):
    """Get table structure information"""
    try:
        cursor = connection.cursor(dictionary=True)

        # Get table structure
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()

        # Get row count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count_result = cursor.fetchone()
        row_count = count_result['count'] if count_result else 0

        cursor.close()

        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "row_count": row_count
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table info: {str(e)}")

@app.get("/api/employees/sample")
async def get_sample_employees(
    limit: int = 10,
    connection=Depends(get_db_connection)
):
    """Get sample employee data"""
    try:
        cursor = connection.cursor(dictionary=True)
        query = f"""
            SELECT
                e.emp_no,
                e.first_name,
                e.last_name,
                e.gender,
                e.hire_date,
                d.dept_name,
                t.title,
                s.salary
            FROM employees e
            LEFT JOIN current_dept_emp de ON e.emp_no = de.emp_no
            LEFT JOIN departments d ON de.dept_no = d.dept_no
            LEFT JOIN titles t ON e.emp_no = t.emp_no AND t.to_date IS NULL
            LEFT JOIN salaries s ON e.emp_no = s.emp_no
            ORDER BY e.emp_no
            LIMIT {limit}
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/api/departments")
async def get_departments(connection=Depends(get_db_connection)):
    """Get all departments"""
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM departments")
        results = cursor.fetchall()
        cursor.close()

        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/api/stats")
async def get_database_stats(connection=Depends(get_db_connection)):
    """Get database statistics"""
    try:
        cursor = connection.cursor(dictionary=True)

        stats = {}

        # Employee count
        cursor.execute("SELECT COUNT(*) as count FROM employees")
        stats['total_employees'] = cursor.fetchone()['count']

        # Department count
        cursor.execute("SELECT COUNT(*) as count FROM departments")
        stats['total_departments'] = cursor.fetchone()['count']

        # Average salary
        cursor.execute("SELECT AVG(salary) as avg_salary FROM salaries WHERE to_date = '9999-01-01'")
        stats['average_salary'] = round(cursor.fetchone()['avg_salary'], 2)

        # Gender distribution
        cursor.execute("SELECT gender, COUNT(*) as count FROM employees GROUP BY gender")
        stats['gender_distribution'] = cursor.fetchall()

        cursor.close()

        return {
            "success": True,
            "stats": stats
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
