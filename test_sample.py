#!/usr/bin/env python3
"""
Test script to create a sample PDF resume for testing the PDF parsing functionality.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import requests
import os

def create_test_pdf():
    """Create a simple test PDF resume."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()
    
    c = canvas.Canvas(temp_path, pagesize=letter)
    width, height = letter
    
    # Add content to PDF
    y_position = height - 50
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_position, "Jane Smith")
    y_position -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Senior Python Developer")
    y_position -= 20
    c.drawString(50, y_position, "Email: jane.smith@example.com")
    y_position -= 20
    c.drawString(50, y_position, "Phone: +1-555-987-6543")
    y_position -= 40
    
    # Skills
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "SKILLS")
    y_position -= 20
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Python, FastAPI, Docker, PostgreSQL, AWS, React")
    y_position -= 40
    
    # Education
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "EDUCATION")
    y_position -= 20
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Master of Science in Computer Science")
    y_position -= 15
    c.drawString(50, y_position, "Stanford University (2019-2021)")
    y_position -= 40
    
    # Experience
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "EXPERIENCE")
    y_position -= 20
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Senior Python Developer - TechCorp Inc")
    y_position -= 15
    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, "• Led development of REST APIs serving 1M+ requests daily")
    y_position -= 15
    c.drawString(50, y_position, "• Implemented microservices architecture using FastAPI")
    y_position -= 30
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Software Engineer - WebSolutions Ltd")
    y_position -= 15
    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, "• Developed web applications using Python and Django")
    y_position -= 15
    c.drawString(50, y_position, "• Collaborated with cross-functional teams")
    
    c.save()
    return temp_path

def test_pdf_endpoint(pdf_path):
    """Test the PDF parsing endpoint."""
    url = "http://localhost:7861/parse-pdf"
    
    with open(pdf_path, 'rb') as f:
        files = {'file': ('test_resume.pdf', f, 'application/pdf')}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        print("✅ PDF parsing successful!")
        result = response.json()
        print(f"📄 Filename: {result.get('filename')}")
        print(f"📊 Source: {result.get('source')}")
        
        parsing_result = result.get('parsing_result', {})
        print(f"\n👤 Name: {parsing_result.get('name')}")
        print(f"📧 Email: {parsing_result.get('email')}")
        print(f"📱 Phone: {parsing_result.get('mobile_number')}")
        print(f"🎯 Skills: {parsing_result.get('skills')}")
        print(f"🎓 Education: {parsing_result.get('education')}")
        print(f"💼 Experience: {parsing_result.get('experience')}")
        
    else:
        print(f"❌ PDF parsing failed with status {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    # Check if reportlab is available
    try:
        print("Creating test PDF...")
        pdf_path = create_test_pdf()
        print(f"Test PDF created at: {pdf_path}")
        
        print("\nTesting PDF parsing endpoint...")
        test_pdf_endpoint(pdf_path)
        
        # Cleanup
        os.unlink(pdf_path)
        print("\nTest PDF cleaned up.")
        
    except ImportError:
        print("❌ reportlab not installed. Install with: pip install reportlab")
        print("Testing with curl command instead...")
        
        # Alternative test with curl
        print("\nYou can test PDF parsing manually with:")
        print("curl -X POST http://localhost:7861/parse-pdf -F 'file=@your_resume.pdf'")
