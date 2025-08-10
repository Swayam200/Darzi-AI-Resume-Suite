import uvicorn
import tempfile
import os
from fastmcp import Client
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from utils import ResumeParser


MCP_ENDPOINT = "https://vit-bhopal-ai-innovators-hub-darzi-mcp-server.hf.space/mcp/"

app = FastAPI(title="Darzi Backend API")
origins = ["*"] # needs to changed in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize local parser
resume_parser = ResumeParser()


client: Optional[Client] = None

@app.on_event("startup")
async def startup():
    global client
    client = Client(MCP_ENDPOINT)
    await client.__aenter__()

@app.on_event("shutdown")
async def shutdown():
    global client
    if client:
        await client.__aexit__(None, None, None)
        client = None

@app.post("/parse")
async def parse_plain(request: Request):
    """Parse plain text resume using both local parser and MCP server"""
    body_bytes = await request.body()
    text = body_bytes.decode("utf-8").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty body; send raw text with Content-Type: text/plain")

    # Use local parser for text-based parsing
    try:
        # Parse using local parser methods directly on text
        local_result = {
            "name": resume_parser.extract_name(text),
            "email": resume_parser.extract_email(text),
            "mobile_number": resume_parser.extract_phone(text),
            "skills": resume_parser.extract_skills(text),
            "education": resume_parser.extract_education(text),
            "experience": resume_parser.extract_experience(text),
            "raw_text": text[:500] + "..." if len(text) > 500 else text
        }
        
        # Try to enhance with MCP if available
        try:
            mcp_result = await client.call_tool("extract_data", {"text": text})
            return {
                "local_parsing": local_result,
                "mcp_parsing": mcp_result,
                "source": "hybrid"
            }
        except Exception as mcp_error:
            print(f"MCP parsing failed: {mcp_error}")
            return {
                "local_parsing": local_result,
                "mcp_parsing": None,
                "source": "local_only",
                "mcp_error": str(mcp_error)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """Parse PDF resume file and extract structured data"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Parse the PDF using local parser
        result = resume_parser.parse_resume(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "filename": file.filename,
            "parsing_result": result,
            "source": "local_parser"
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"PDF parsing failed: {str(e)}")


if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860)