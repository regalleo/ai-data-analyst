"""
Chart auto-selection and generation agent.
Uses LLM reasoning to determine best visualization for user questions.
"""
import json
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel


class ChartRecommendation(BaseModel):
    """Structured chart recommendation from the agent."""
    chart_type: str  # pie, bar, line, heatmap, scatter, table
    reason: str  # Explanation of why this chart type was chosen
    data: Dict[str, Any]  # Data structure for frontend
    title: str  # Chart title
    x_label: Optional[str] = None
    y_label: Optional[str] = None


# Chart type options with reasoning hints
CHART_TYPES = {
    "bar": "Best for comparing categories or showing distributions",
    "line": "Best for trends over time or continuous data",
    "pie": "Best for showing proportions of a whole",
    "scatter": "Best for showing correlations between two variables",
    "heatmap": "Best for showing intensity patterns in 2D data",
    "table": "Best for detailed numerical comparisons"
}


def create_chart_prompt() -> str:
    """Create the system prompt for chart selection."""
    return """You are a senior data analyst. Given a user's question and dataset schema,
you must recommend the best visualization.

Dataset Schema:
{schema}

User Question: {question}

Consider:
1. What is the analytical intent? (comparison, trend, distribution, correlation, proportion)
2. What data types are involved? (categorical, numerical, temporal)
3. How many variables? (1, 2, or many)

Available chart types: {chart_types}

Return ONLY a valid JSON object with these fields:
- chart_type: One of the available chart types
- reason: Why this chart type fits the question (2-3 sentences)
- title: Descriptive title for the chart
- x_label: Label for x-axis (if applicable, otherwise null)
- y_label: Label for y-axis (if applicable, otherwise null)

Example response:
{{"chart_type": "bar", "reason": "Comparing sales across regions requires showing categorical data with numerical values. A bar chart clearly shows the comparison between different regions.", "title": "Sales by Region", "x_label": "Region", "y_label": "Sales ($)"}}

Do NOT include any markdown formatting, code blocks, or extra text. Return ONLY the JSON object.
"""


def run_chart_agent(
    question: str,
    schema: Dict[str, Any],
    llm: Optional[ChatGroq] = None
) -> ChartRecommendation:
    """
    Generate chart recommendation using LLM reasoning.
    
    Args:
        question: User's analytical question
        schema: Dataset schema with column info
        llm: Optional LLM instance (creates default if not provided)
        
    Returns:
        ChartRecommendation with type, reason, and data structure
    """
    if llm is None:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
        )
    
    # Format schema for prompt
    schema_str = json.dumps(schema, indent=2)
    
    prompt = PromptTemplate.from_template(create_chart_prompt())
    formatted_prompt = prompt.format(
        schema=schema_str,
        question=question,
        chart_types=", ".join(CHART_TYPES.keys())
    )
    
    try:
        response = llm.predict(formatted_prompt)
        
        # Clean response (remove markdown if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response.replace("```json", "").replace("```", "").strip()
        elif response.startswith("```"):
            response = response.replace("```", "").strip()
        
        # Parse JSON response
        data = json.loads(response)
        
        return ChartRecommendation(
            chart_type=data.get("chart_type", "table"),
            reason=data.get("reason", "Default table view"),
            data=_create_chart_data_structure(data.get("chart_type", "table"), schema),
            title=data.get("title", question),
            x_label=data.get("x_label"),
            y_label=data.get("y_label")
        )
        
    except json.JSONDecodeError as e:
        # Fallback to table view on parsing error
        return ChartRecommendation(
            chart_type="table",
            reason=f"Failed to parse LLM response. Defaulting to table view.",
            data={"type": "table"},
            title=question,
            x_label=None,
            y_label=None
        )
    except Exception as e:
        return ChartRecommendation(
            chart_type="table",
            reason=f"Chart generation error. Showing raw data in table format.",
            data={"type": "table"},
            title=question,
            x_label=None,
            y_label=None
        )


def _create_chart_data_structure(chart_type: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a data structure template based on chart type and schema.
    
    Args:
        chart_type: Type of chart to create
        schema: Dataset schema
        
    Returns:
        Data structure template for the frontend
    """
    # Extract column information
    all_columns = []
    for table_info in schema.values():
        if "columns" in table_info:
            all_columns.extend(table_info["columns"])
    
    base_structure = {
        "type": chart_type,
        "columns": all_columns[:10],  # Limit to first 10 columns
    }
    
    if chart_type == "bar":
        return {
            **base_structure,
            "requires": ["category_column", "value_column"],
            "description": "Bar chart for categorical comparisons"
        }
    elif chart_type == "line":
        return {
            **base_structure,
            "requires": ["x_axis_column", "y_axis_column"],
            "description": "Line chart for trends over time"
        }
    elif chart_type == "pie":
        return {
            **base_structure,
            "requires": ["label_column", "value_column"],
            "description": "Pie chart for proportions"
        }
    elif chart_type == "scatter":
        return {
            **base_structure,
            "requires": ["x_column", "y_column"],
            "description": "Scatter plot for correlations"
        }
    elif chart_type == "heatmap":
        return {
            **base_structure,
            "requires": ["x_column", "y_column", "value_column"],
            "description": "Heatmap for intensity patterns"
        }
    else:  # table
        return {
            **base_structure,
            "requires": [],
            "description": "Table for detailed data view"
        }


def extract_chart_data(
    sql_results: list,
    columns: list
) -> Dict[str, Any]:
    """
    Convert SQL results to format usable by chart visualization.
    
    Args:
        sql_results: List of dictionaries from SQL query
        columns: Column names
        
    Returns:
        Data structure suitable for chart generation
    """
    if not sql_results or not columns:
        return {"data": [], "columns": []}
    
    # Extract unique values for categorical columns
    categorical_cols = []
    numeric_cols = []
    
    if sql_results:
        sample = sql_results[0]
        for col in columns:
            val = sample.get(col)
            if isinstance(val, (int, float)):
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
    
    return {
        "data": sql_results,
        "columns": columns,
        "categorical": categorical_cols,
        "numeric": numeric_cols,
        "row_count": len(sql_results)
    }


def generate_chart_config(
    recommendation: ChartRecommendation,
    sql_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate chart configuration for frontend rendering.
    
    Args:
        recommendation: Chart recommendation from agent
        sql_data: Data from SQL query
        
    Returns:
        Complete chart configuration
    """
    return {
        "chart_type": recommendation.chart_type,
        "title": recommendation.title,
        "data": sql_data.get("data", []),
        "columns": sql_data.get("columns", []),
        "x_label": recommendation.x_label,
        "y_label": recommendation.y_label,
        "reason": recommendation.reason,
        "categorical_columns": sql_data.get("categorical", []),
        "numeric_columns": sql_data.get("numeric", []),
    }