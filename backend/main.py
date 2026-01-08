"""
Main FastAPI application for AI Data Analyst.
Production-ready API with multi-tenant data isolation.
"""

import os
import sys
import traceback
from dotenv import load_dotenv

from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np  # ✅ Add this import
import uuid
import re
import json
import logging

load_dotenv()
os.environ["TRANSFORMERS_NO_TF"] = "1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import get_db, engine
from models import Base, User, Dataset
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from rag import build_rag_index, delete_rag_index
from agent import build_agent
from data_cleaner import analyze_data_quality, clean_dataset, get_cleaning_preview, export_cleaned_data


# ==================== CUSTOM JSON ENCODER ====================

def convert_numpy_types(obj):
    """
    Recursively convert numpy/pandas types to native Python types.
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict()
    elif pd.isna(obj):
        return None
    else:
        return obj


class NumpyJSONResponse(JSONResponse):
    """Custom JSON response that handles numpy types."""
    def render(self, content: Any) -> bytes:
        # Convert numpy types before rendering
        content = convert_numpy_types(content)
        return super().render(content)


# -------------------- DB INIT --------------------
Base.metadata.create_all(bind=engine)

# -------------------- APP --------------------
app = FastAPI(
    title="AI Data Analyst API",
    description="Multi-tenant AI analytics platform with hybrid RAG",
    version="1.0.0",
    default_response_class=NumpyJSONResponse,  # ✅ Use custom response class
)

# Rest of your code remains the same...
# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- GLOBAL EXCEPTION HANDLER --------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, FastAPIHTTPException):
        raise exc
    logger.error(traceback.format_exc())
    return NumpyJSONResponse(  # ✅ Use custom response
        status_code=500,
        content={"detail": "Internal server error"},
    )

# ... rest of your schemas and endpoints ...


# ==================== SCHEMAS ====================


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DatasetUploadResponse(BaseModel):
    id: int
    name: str
    table_name: str
    columns: List[str]
    message: str
    needs_cleaning: Optional[bool] = False
    quality_issues: Optional[List[str]] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    message: str
    dataset_id: Optional[int] = None


class AskResponse(BaseModel):
    answer: str
    chart_type: Optional[str] = None
    chart_data: Optional[List[dict]] = None
    columns: Optional[List[str]] = None
    chart_reason: Optional[str] = None
    kpis: Optional[List[Dict[str, Any]]] = None  # KPI cards
    charts: Optional[List[Dict[str, Any]]] = None  # Multiple charts
    filters: Optional[Dict[str, List[Any]]] = None  # Available filters


# ==================== AUTH ====================


@app.post("/api/v1/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/v1/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}


# ==================== DATASETS ====================


def sanitize_table_name(name: str) -> str:
    """Sanitize table name to be SQL-safe."""
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name.replace(" ", "_"))
    if not name[0].isalpha():
        name = f"tbl_{name}"
    return f"{name}_{uuid.uuid4().hex[:8]}"


@app.post("/api/v1/datasets/upload", response_model=DatasetUploadResponse)
def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files supported")

        df = pd.read_csv(file.file)

        # Analyze data quality
        quality_report = analyze_data_quality(df)

        columns = df.columns.tolist()
        schema_info = {
            "columns": columns,
            "row_count": len(df),
            "quality_report": quality_report,
        }

        table_name = sanitize_table_name(file.filename)

        dataset = Dataset(
            name=file.filename,
            table_name=table_name,
            owner_id=current_user.id,
            schema_info=json.dumps(schema_info),
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

        # Write dataframe to SQL
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)

        # Build RAG index
        build_rag_index(
            current_user.id,
            [f"Dataset {file.filename} with columns: {', '.join(columns)}"],
        )

        return DatasetUploadResponse(
            id=dataset.id,
            name=dataset.name,
            table_name=dataset.table_name,
            columns=columns,
            message="Dataset uploaded successfully",
            needs_cleaning=quality_report.get("needs_cleaning", False),
            quality_issues=quality_report.get("issues", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading dataset: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Error uploading dataset: {str(e)}"
        )


@app.get("/api/v1/datasets")
def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).all()

    result = []
    for d in datasets:
        schema_info = json.loads(d.schema_info) if d.schema_info else {}
        result.append(
            {
                "id": d.id,
                "name": d.name,
                "table_name": d.table_name,
                "columns": schema_info.get("columns", []),
            }
        )

    return result


@app.delete("/api/v1/datasets/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id)
        .first()
    )

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Delete the table from database (SQLite compatible)
    try:
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {dataset.table_name}"))
    except Exception as e:
        logger.warning(f"Could not drop table {dataset.table_name}: {e}")

    # Delete from database
    db.delete(dataset)
    db.commit()

    # Delete from RAG index
    delete_rag_index(current_user.id)

    return {"message": "Dataset deleted successfully"}


# ==================== DATA CLEANING ====================


@app.get("/api/v1/datasets/{dataset_id}/preview-cleaning")
def preview_cleaning(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a preview of what cleaning will do to a dataset.
    """
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id)
        .first()
    )

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        # Read data from SQL table
        df = pd.read_sql(f"SELECT * FROM {dataset.table_name}", con=engine)
        
        # Get cleaning preview
        preview = get_cleaning_preview(df)
        
        return preview
    except Exception as e:
        logger.error(f"Error generating cleaning preview: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")


@app.post("/api/v1/datasets/{dataset_id}/clean")
def clean_dataset_endpoint(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Clean a dataset and update it in the database.
    """
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id)
        .first()
    )

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        # Read data from SQL table
        df = pd.read_sql(f"SELECT * FROM {dataset.table_name}", con=engine)
        
        # Clean the dataset
        cleaned_df, report = clean_dataset(df)
        
        # Update the SQL table with cleaned data
        cleaned_df.to_sql(dataset.table_name, con=engine, if_exists="replace", index=False)
        
        # Update schema_info in database
        schema_info = json.loads(dataset.schema_info) if dataset.schema_info else {}
        schema_info["columns"] = cleaned_df.columns.tolist()
        schema_info["row_count"] = int(len(cleaned_df))
        
        # Re-analyze quality
        new_quality = analyze_data_quality(cleaned_df)
        schema_info["quality_report"] = new_quality
        
        dataset.schema_info = json.dumps(schema_info)
        db.commit()
        
        # Convert report to dict and clean numpy types
        report_dict = report.to_dict()
        
        # Return with automatic numpy conversion via NumpyJSONResponse
        return {
            "message": "Dataset cleaned successfully",
            "report": report_dict,
            "rows_after": int(len(cleaned_df)),
            "columns_after": int(len(cleaned_df.columns)),
        }
    except Exception as e:
        logger.error(f"Error cleaning dataset: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error cleaning dataset: {str(e)}")


@app.get("/api/v1/datasets/{dataset_id}/download-cleaned")
def download_cleaned_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Download a cleaned dataset as CSV.
    """
    from fastapi.responses import StreamingResponse
    import io
    
    dataset = (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id)
        .first()
    )

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        # Read data from SQL table
        df = pd.read_sql(f"SELECT * FROM {dataset.table_name}", con=engine)
        
        # Clean the dataset
        cleaned_df, _ = clean_dataset(df)
        
        # Export to CSV
        csv_buffer = io.BytesIO()
        cleaned_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        filename = f"cleaned_{dataset.name}"
        
        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error downloading cleaned dataset: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error downloading dataset: {str(e)}")


# ==================== HELPER FUNCTIONS ====================


def _generate_kpis(data: List[dict], columns: List[str], dataset_name: str) -> List[Dict[str, Any]]:
    """Generate KPI cards from data."""
    if not data or not columns:
        return []
    
    kpis = []
    
    # Total Records KPI
    kpis.append({
        "title": f"Total {dataset_name.replace('.csv', '')}",
        "value": str(len(data)),
        "icon": "database",
        "trend": "neutral"
    })
    
    # Numeric Column KPIs
    numeric_columns = []
    for col in columns:
        if data and isinstance(data[0].get(col), (int, float)):
            numeric_columns.append(col)
    
    for col in numeric_columns[:2]:  # Max 2 numeric KPIs
        values = [row[col] for row in data if row.get(col) is not None]
        if values:
            total = sum(values)
            avg = total / len(values)
            
            # Total KPI
            if len(kpis) < 6:
                kpis.append({
                    "title": f"Total {col}",
                    "value": f"${total:,.2f}" if "price" in col.lower() else f"{total:,.0f}",
                    "icon": "dollar-sign" if "price" in col.lower() else "hash",
                    "trend": "neutral"
                })
            
            # Average KPI
            if len(kpis) < 6:
                kpis.append({
                    "title": f"Avg {col}",
                    "value": f"${avg:,.2f}" if "price" in col.lower() else f"{avg:,.2f}",
                    "icon": "trending-up",
                    "trend": "neutral"
                })
    
    # Categorical Diversity KPI
    categorical_columns = [col for col in columns if col not in numeric_columns]
    if categorical_columns and len(kpis) < 6:
        col = categorical_columns[0]
        unique_values = len(set(row[col] for row in data if row.get(col)))
        kpis.append({
            "title": f"Unique {col}",
            "value": str(unique_values),
            "icon": "users" if "vendor" in col.lower() else "tag",
            "trend": "neutral"
        })
    
    return kpis[:6]  # Max 6 KPIs


def _extract_filter_options(data: List[dict], columns: List[str]) -> Dict[str, List[Any]]:
    """Extract unique values for each column to enable filtering."""
    filters = {}
    
    for col in columns:
        unique_values = list(set(row[col] for row in data if row.get(col) is not None))
        # Only include if reasonable number of unique values
        if 1 < len(unique_values) <= 50:
            filters[col] = sorted(unique_values)[:20]  # Max 20 filter options per column
    
    return filters


# ==================== CHAT ====================


class ChartRequest(BaseModel):
    query: str
    dataset_id: Optional[int] = None


class ChartResponse(BaseModel):
    chart_type: str
    data: List[dict]
    columns: List[str]
    title: str
    x_label: Optional[str] = None
    y_label: Optional[str] = None


@app.post("/api/v1/chat", response_model=AskResponse)
def chat(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Get user's datasets
        query = db.query(Dataset).filter(Dataset.owner_id == current_user.id)

        if request.dataset_id:
            query = query.filter(Dataset.id == request.dataset_id)

        datasets = query.all()

        if not datasets:
            raise HTTPException(status_code=400, detail="No datasets uploaded")

        # Build and run agent
        agent = build_agent(
            db=db,
            user=current_user,
            datasets=datasets,
        )

        # Custom callback
        from langchain.callbacks.base import BaseCallbackHandler
        
        class CustomCallback(BaseCallbackHandler):
            def __init__(self):
                self.sql_data = None
                self.chart_config = None
            
            def on_tool_end(self, output: str, **kwargs) -> None:
                tool_name = kwargs.get('name', '')
                logger.info(f"Tool '{tool_name}' completed")
                
                if tool_name == 'sql_analyzer':
                    try:
                        result = json.loads(output)
                        if result.get('success'):
                            self.sql_data = result
                            logger.info(f"✓ Captured SQL data: {len(result.get('rows', []))} rows")
                    except Exception as e:
                        logger.error(f"Failed to parse SQL output: {e}")
                
                elif tool_name == 'chart_generator':
                    try:
                        result = json.loads(output)
                        if result.get('success'):
                            self.chart_config = result
                            logger.info(f"✓ Captured chart config: {result.get('chart_type')}")
                    except Exception as e:
                        logger.error(f"Failed to parse chart output: {e}")
        
        callback = CustomCallback()
        
        # Invoke agent with better error handling
        try:
            result = agent.invoke(
                {"input": request.message}, 
                config={
                    "callbacks": [callback],
                    "max_iterations": 10,
                }
            )
        except Exception as agent_error:
            logger.error(f"Agent invocation failed: {str(agent_error)}")
            # Fallback response
            return AskResponse(
                answer=f"I encountered an error processing your request. Please try rephrasing your question or check if your dataset is properly uploaded. Error: {str(agent_error)[:200]}",
                chart_type=None,
                chart_data=None,
                columns=None,
            )
        
        # Extract answer
        if isinstance(result, dict):
            answer = result.get("output", str(result))
        else:
            answer = str(result)

        # Rest of your code remains the same...
        chart_type = None
        chart_data = None
        columns = None
        chart_reason = None
        kpis = None
        available_filters = None
        
        if callback.sql_data:
            chart_data = callback.sql_data.get("rows", [])
            columns = callback.sql_data.get("columns", [])
            
            if chart_data and len(chart_data) > 0:
                kpis = _generate_kpis(chart_data, columns, datasets[0].name if datasets else "Dataset")
            
            if chart_data and columns:
                available_filters = _extract_filter_options(chart_data, columns)
        
        if callback.chart_config:
            chart_type = callback.chart_config.get("chart_type")
            chart_reason = callback.chart_config.get("reason")

        if chart_data and not chart_type:
            chart_type = "bar"

        return AskResponse(
            answer=answer,
            chart_type=chart_type,
            chart_data=chart_data,
            columns=columns,
            chart_reason=chart_reason,
            kpis=kpis,
            filters=available_filters
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/api/v1/visualize", response_model=ChartResponse)
def visualize(
    request: ChartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a visualization for the given query.
    Returns chart configuration and data ready for frontend rendering.
    """
    try:
        # Get user's datasets
        query = db.query(Dataset).filter(Dataset.owner_id == current_user.id)

        if request.dataset_id:
            query = query.filter(Dataset.id == request.dataset_id)

        datasets = query.all()

        if not datasets:
            raise HTTPException(status_code=400, detail="No datasets uploaded")

        # Build schema info
        schema_info = {}
        for d in datasets:
            parsed = {}
            if d.schema_info:
                try:
                    parsed = json.loads(d.schema_info)
                except Exception:
                    pass
            schema_info[d.table_name] = {
                "columns": parsed.get("columns", []),
                "row_count": parsed.get("row_count", 0),
            }

        # Get chart recommendation
        from chart_agent import run_chart_agent
        chart_rec = run_chart_agent(request.query, schema_info)

        # Execute SQL to get actual data
        from sql_tool import run_safe_sql
        allowed_tables = [d.table_name for d in datasets]
        
        # Try to extract a simple query from the request
        # For now, just get all data from the first table
        table_name = allowed_tables[0]
        sql_query = f"SELECT * FROM {table_name}"
        
        rows, columns = run_safe_sql(db, sql_query, allowed_tables, current_user.id)

        return ChartResponse(
            chart_type=chart_rec.chart_type,
            data=rows,
            columns=columns,
            title=chart_rec.title,
            x_label=chart_rec.x_label,
            y_label=chart_rec.y_label,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Visualization failed: {str(e)}")


# ==================== HEALTH ====================


@app.get("/")
def health():
    return {"status": "ok", "service": "AI Data Analyst"}


# ==================== STARTUP ====================


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    groq_key_set = bool(os.getenv("GROQ_API_KEY"))
    logger.info(f"🚀 AI Data Analyst API starting...")
    logger.info(f"✓ GROQ_API_KEY loaded: {groq_key_set}")
    if not groq_key_set:
        logger.warning("⚠️  GROQ_API_KEY not found in environment!")