import io
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utils.parser import parse_resume
from utils.ai_engine import evaluate_resume_with_ai
from utils.roadmap_generator import generate_pdf_report
from utils.job_matcher import match_job_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CareerPilot AI API")

# Mock file-like object to bridge FastAPI UploadFile and parse_resume parser helper
class MockFile(io.BytesIO):
    def __init__(self, file_bytes, filename):
        super().__init__(file_bytes)
        self.name = filename

from typing import Optional

# Models for JSON request payloads
class MatchRequest(BaseModel):
    cv_text: str
    job_description: str
    custom_api_key: Optional[str] = None

class PDFRequest(BaseModel):
    analysis: dict
    target_role: str

@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    custom_api_key: str = Form(None)
):
    try:
        logger.info(f"Received file upload: {file.filename} for role: {target_role}")
        file_bytes = await file.read()
        mock_file = MockFile(file_bytes, file.filename)
        cv_text = parse_resume(mock_file)
        
        # Run AI evaluation utilizing our upgraded engine
        analysis = evaluate_resume_with_ai(cv_text, target_role, custom_api_key or None)
        
        return JSONResponse(content={
            "cv_text": cv_text,
            "target_role": target_role,
            "analysis": analysis
        })
    except Exception as e:
        logger.error(f"Error during analysis endpoint execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match")
async def match_resume(req: MatchRequest):
    try:
        logger.info("Received job description matching request.")
        match_result = match_job_description(req.cv_text, req.job_description, req.custom_api_key or None)
        return JSONResponse(content=match_result)
    except Exception as e:
        logger.error(f"Error during job matching endpoint execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-pdf")
async def generate_pdf(req: PDFRequest):
    try:
        logger.info(f"Generating PDF for role: {req.target_role}")
        pdf_buffer = generate_pdf_report(req.analysis, req.target_role)
        pdf_bytes = pdf_buffer.getvalue()
        
        safe_role = req.target_role.replace(" ", "_")
        filename = f"CareerPilot_{safe_role}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        logger.error(f"Error during PDF generation endpoint execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve assets folder
assets_dir = os.path.join(os.path.dirname(__file__), "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Serve static frontend files (homepage, css, js)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    logger.warning("Static assets directory 'static' not found yet. Front-end will not load until static folder is built.")
