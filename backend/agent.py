"""
AI Agent module using LangChain 0.2.x + Groq
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
import json

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from models import User, Dataset
from sql_tool import run_safe_sql
from rag import query_rag_index
from chart_agent import run_chart_agent


import logging

logger = logging.getLogger(__name__)


# Add this to your tool creation to fix the Groq error
def _create_sql_tool(db: Session, allowed_tables: List[str], user: User):
    def run_query(query: str) -> str:
        """Execute a SQL query and return results as JSON."""
        try:
            logger.info(f"Executing SQL: {query}")
            rows, columns = run_safe_sql(db, query, allowed_tables, user.id)

            # Limit rows for large results
            limited_rows = rows[:100] if len(rows) > 100 else rows

            result = {
                "success": True,
                "columns": columns,
                "rows": limited_rows,
                "row_count": len(limited_rows),
                "total_rows": len(rows),
                "truncated": len(rows) > 100,
            }
            json_result = json.dumps(result, indent=2, default=str)
            logger.info(f"SQL Result: {len(rows)} rows, {len(columns)} columns")
            return json_result
        except Exception as e:
            logger.error(f"SQL Error: {str(e)}")
            error_result = {
                "success": False,
                "error": str(e),
                "message": "Query failed. Check your SQL syntax and table names.",
            }
            return json.dumps(error_result)

    return run_query


# =====================================================
# TOOL INPUT SCHEMAS
# =====================================================


class SQLQueryInput(BaseModel):
    """Input schema for SQL query tool."""

    query: str = Field(description="A valid SQL SELECT query to execute")


class RAGSearchInput(BaseModel):
    """Input schema for RAG search tool."""

    query: str = Field(description="Search query to find schema information")


class ChartGeneratorInput(BaseModel):
    """Input schema for chart generator tool."""

    question: str = Field(description="Question about what to visualize")


# =====================================================
# AGENT BUILDER
# =====================================================


def build_agent(
    db: Session,
    user: User,
    datasets: List[Dataset],
):
    """
    Build a Groq-powered agent using tool calling (LangChain 0.2.x compatible).
    """

    allowed_tables = [d.table_name for d in datasets]
    schema_info = _build_schema_info(datasets)

    # ✅ Groq LLM (reads GROQ_API_KEY from .env)
    # Using llama-3.3-70b-versatile (current production model as of Jan 2025)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
    )

    # ===================== TOOLS ======================

    tools = [
        StructuredTool.from_function(
            func=_create_sql_tool(db, allowed_tables, user),
            name="sql_analyzer",
            description=f"Execute SQL queries to fetch actual data for visualization. Use this FIRST to get the data, then use chart_generator. Available tables: {', '.join(allowed_tables)}. Always include columns needed for charts (e.g., category and value columns).",
            args_schema=SQLQueryInput,
        ),
        StructuredTool.from_function(
            func=_create_rag_tool(user.id, schema_info),
            name="hybrid_rag",
            description="Get table schema and column information. Use this if you need to check available columns before writing SQL queries.",
            args_schema=RAGSearchInput,
        ),
        StructuredTool.from_function(
            func=_create_chart_tool(schema_info),
            name="chart_generator",
            description="Generate chart recommendation AFTER fetching data with sql_analyzer. This determines the chart type (bar, pie, line, etc.) based on the data structure and user's question.",
            args_schema=ChartGeneratorInput,
        ),
    ]

    # Format schema info for prompt
    schema_text = ""
    for table_name, info in schema_info.items():
        columns = info.get("columns", [])
        row_count = info.get("row_count", 0)
        schema_text += f"\nTable: {table_name}\n"
        schema_text += f"Columns: {', '.join(columns)}\n"
        schema_text += f"Rows: {row_count}\n"

    # ===================== PROMPT ======================

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You are an expert AI Data Analyst that helps users analyze data.

AVAILABLE DATA:
{schema_text}

YOUR TOOLS:
1. sql_analyzer - Execute SQL queries to fetch data
2. hybrid_rag - Get schema information
3. chart_generator - Recommend chart types

IMPORTANT RULES:
- ALWAYS use sql_analyzer to get actual data before making conclusions
- When asked for visualizations, use sql_analyzer FIRST, then chart_generator
- Return data in your final response, not just descriptions
- Keep SQL queries simple and focused
- Use proper SQL syntax for the available tables

EXAMPLE WORKFLOW for "Show me products by price":
1. Call sql_analyzer with: SELECT productName, Price FROM table_name ORDER BY Price DESC LIMIT 20
2. Call chart_generator with: "bar chart of products by price"
3. Provide a summary with the data you retrieved""",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # ===================== CREATE AGENT ======================

    try:
        agent = create_tool_calling_agent(llm, tools, prompt)
    except Exception as e:
        # Fallback to manual agent creation
        from langchain.agents.format_scratchpad.openai_tools import (
            format_to_openai_tool_messages,
        )
        from langchain.agents.output_parsers.openai_tools import (
            OpenAIToolsAgentOutputParser,
        )

        llm_with_tools = llm.bind_tools(tools)

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )

    # ===================== CREATE EXECUTOR ======================

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15,
        return_intermediate_steps=False,
    )


# =====================================================
# TOOL FACTORIES
# =====================================================


def _create_sql_tool(db: Session, allowed_tables: List[str], user: User):
    def run_query(query: str) -> str:
        """Execute a SQL query and return results as JSON."""
        try:
            # Pass owner_id if run_safe_sql requires it
            rows, columns = run_safe_sql(db, query, allowed_tables, user.id)

            # Limit rows for large results
            limited_rows = rows[:100] if len(rows) > 100 else rows

            result = {
                "success": True,
                "columns": columns,
                "rows": limited_rows,
                "row_count": len(limited_rows),
                "total_rows": len(rows),
                "truncated": len(rows) > 100,
            }
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Query failed. Check your SQL syntax and table names.",
                }
            )

    return run_query


def _create_rag_tool(user_id: int, schema_info: Dict[str, Any]):
    def search_docs(query: str) -> str:
        """Search documentation for schema information."""
        try:
            docs = query_rag_index(user_id, query)
            if docs:
                return "\n\n".join(docs)
            else:
                # Fallback to schema_info if RAG index is not available
                schema_text = "Available tables and columns:\n\n"
                for table_name, info in schema_info.items():
                    columns = info.get("columns", [])
                    row_count = info.get("row_count", 0)
                    schema_text += f"Table: {table_name}\n"
                    schema_text += f"Columns: {', '.join(columns)}\n"
                    schema_text += f"Row count: {row_count}\n\n"
                return schema_text
        except Exception as e:
            # Even on error, return schema info
            schema_text = "Available tables and columns:\n\n"
            for table_name, info in schema_info.items():
                columns = info.get("columns", [])
                row_count = info.get("row_count", 0)
                schema_text += f"Table: {table_name}\n"
                schema_text += f"Columns: {', '.join(columns)}\n"
                schema_text += f"Row count: {row_count}\n\n"
            return schema_text

    return search_docs


def _create_chart_tool(schema_info: Dict[str, Any]):
    def generate_chart(question: str) -> str:
        """Generate chart recommendations."""
        try:
            rec = run_chart_agent(question, schema_info)
            result = {
                "success": True,
                "chart_type": rec.chart_type,
                "reason": rec.reason,
                "data": rec.data,
                "title": rec.title,
                "x_label": rec.x_label,
                "y_label": rec.y_label,
            }
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to generate chart recommendation.",
                }
            )

    return generate_chart


# =====================================================
# SCHEMA BUILDER
# =====================================================


def _build_schema_info(datasets: List[Dataset]) -> Dict[str, Any]:
    """Build schema information from datasets."""
    schema = {}

    for d in datasets:
        parsed = {}
        if d.schema_info:
            try:
                parsed = json.loads(d.schema_info)
            except Exception:
                pass

        schema[d.table_name] = {
            "columns": parsed.get("columns", []),
            "row_count": parsed.get("row_count", 0),
        }

    return schema
