"""
Safe SQL execution tool for the AI agent.
Enforces SELECT-only queries and user table isolation.
"""
from typing import List, Tuple, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from fastapi import HTTPException, status


class SQLSecurityError(Exception):
    """Custom exception for SQL security violations."""
    pass


def validate_query(query: str, allowed_tables: List[str]) -> None:
    """
    Validate that a SQL query is safe to execute.
    """
    query_lower = query.lower().strip()
    
    # Only allow SELECT queries
    if not query_lower.startswith("select"):
        raise SQLSecurityError(
            "Only SELECT queries are allowed for security reasons."
        )
    
    # Check for dangerous SQL patterns
    dangerous_patterns = [
        r'\bdrop\b', r'\btruncate\b', r'\bdelete\b', r'\binsert\b',
        r'\bupdate\b', r'\balter\b', r'\bcreate\b', r'\bgrant\b',
        r'\brevoke\b', r'\bexec\b', r'\bexecute\b', r'\bsp_\w+',
        r'\bxp_\w+', r'\b--', r'\b/\*'
    ]

    import re
    for pattern in dangerous_patterns:
        if re.search(pattern, query_lower):
            raise SQLSecurityError(
                f"Query contains forbidden pattern: {pattern}"
            )

    # Block subqueries for security
    if "select" in query_lower[6:]:
        raise SQLSecurityError(
            "Subqueries are not allowed for security reasons."
        )
    
    # Verify all referenced tables are in allowed list
    if allowed_tables:
        table_pattern = r'\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)\b'
        joins_pattern = r'\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        found_tables = set(re.findall(table_pattern, query_lower))
        found_tables.update(re.findall(joins_pattern, query_lower))
        
        allowed = {t.lower() for t in allowed_tables}

        for table in found_tables:
            if table.lower() not in allowed:
                raise SQLSecurityError(
                    f"Access to table '{table}' is not allowed. "
                    f"Allowed tables: {allowed_tables}"
                )


def get_table_schema(db: Session, table_name: str) -> List[Dict[str, str]]:
    """Get schema information for a table."""
    inspector = inspect(db.bind)
    columns = []

    for col in inspector.get_columns(table_name):
        columns.append({
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col["nullable"],
        })

    return columns


def run_safe_sql(
    db: Session,
    query: str,
    allowed_tables: List[str],
    owner_id: int,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Execute a safe SQL query with validation.
    
    NOTE: owner_id filtering is DISABLED for CSV uploads since those tables
    don't have an owner_id column. Security is enforced at the allowed_tables
    level - users can only query their own tables.
    """
    validate_query(query, allowed_tables)

    query_lower = query.lower()

    # ✅ REMOVED: Auto row-level security injection
    # CSV tables don't have owner_id column, so we rely on allowed_tables filtering instead
    # Security is enforced by only allowing tables that belong to the user
    
    # Force LIMIT if not present
    if "limit" not in query_lower:
        query = f"{query} LIMIT 1000"

    try:
        result = db.execute(text(query))

        column_names = list(result.keys())
        rows = [dict(zip(column_names, row)) for row in result.fetchall()]

        return rows, column_names

    except SQLSecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def suggest_chart_type(
    rows: List[Dict[str, Any]],
    column_names: List[str]
) -> str:
    """
    Suggest appropriate chart type based on data structure.
    """
    if not rows or not column_names:
        return "table"

    date_columns = []
    numeric_columns = []

    for col in column_names:
        value = rows[0].get(col)

        if any(keyword in col.lower() for keyword in ['date', 'time', 'year', 'month', 'day']):
            date_columns.append(col)

        if isinstance(value, (int, float)):
            numeric_columns.append(col)

    if len(numeric_columns) >= 2 and len(date_columns) >= 1:
        return "line"
    elif len(numeric_columns) >= 2:
        return "scatter"
    elif len(numeric_columns) == 1 and len(date_columns) == 1:
        return "bar"
    elif len(numeric_columns) == 1:
        return "pie"

    return "table"


def sql_to_chart_json(
    rows: List[Dict[str, Any]],
    column_names: List[str],
) -> Dict[str, Any]:
    """Convert SQL results to chart-ready JSON format."""
    if not rows:
        return {
            "chart_type": "table",
            "data": [],
            "columns": column_names,
        }

    numeric_cols = [
        col for col in column_names
        if isinstance(rows[0].get(col), (int, float))
    ]

    label_cols = [
        col for col in column_names
        if col not in numeric_cols
    ]

    # Simple bar / line heuristic
    if len(numeric_cols) == 1 and label_cols:
        return {
            "chart_type": "bar",
            "x": label_cols[0],
            "y": numeric_cols[0],
            "data": rows,
        }

    if len(numeric_cols) >= 2:
        return {
            "chart_type": "scatter",
            "x": numeric_cols[0],
            "y": numeric_cols[1],
            "data": rows,
        }

    return {
        "chart_type": "table",
        "data": rows,
        "columns": column_names,
    }


def build_query_feedback(
    query: str,
    rows: List[Dict[str, Any]],
    columns: List[str],
) -> str:
    """Generate human-readable feedback about query results."""
    if not rows:
        return (
            "The query returned no rows. "
            "Try checking filters or using aggregation."
        )

    return (
        f"Query executed successfully.\n"
        f"Returned {len(rows)} rows.\n"
        f"Columns: {', '.join(columns)}.\n"
        f"Sample row: {rows[0]}"
    )