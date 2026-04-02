#!/usr/bin/env python3

import os
import shutil
import tempfile
import requests
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import zipfile
import re
import uvicorn
import json

app = FastAPI(
    title="PDF水印批处理工具",
    description="批量为PDF文件添加水印、重命名并保存到指定目录",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
UPLOAD_FOLDER = 'temp'

# Stirling PDF API configuration
STIRLING_API_BASE = "http://192.168.8.88:18080"
WATERMARK_ENDPOINT = f"{STIRLING_API_BASE}/api/v1/security/add-watermark"

# Ensure temp directory exists
os.makedirs('temp', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Pydantic models for request/response
class ScanFilesRequest(BaseModel):
    paths: List[str]

class ScanFilesResponse(BaseModel):
    success: bool
    files: Optional[List[str]] = None
    count: Optional[int] = None
    error: Optional[str] = None

class PreviewNamingRequest(BaseModel):
    pattern: str
    files: List[str]
    sortType: str = 'filename'

class PreviewItem(BaseModel):
    original: str
    output: str

class PreviewNamingResponse(BaseModel):
    success: bool
    previews: Optional[List[PreviewItem]] = None
    total: Optional[int] = None
    error: Optional[str] = None

class WatermarkConfig(BaseModel):
    text: str
    fontSize: int = 48
    rotation: int = 45
    opacity: int = 10
    color: str = '#808080'
    widthSpacer: int = 50
    heightSpacer: int = 50

class ProcessFilesRequest(BaseModel):
    files: List[str]
    watermark: WatermarkConfig
    namingPattern: str
    sortType: str = 'filename'
    outputDir: str

class ProcessResult(BaseModel):
    original: str
    output: Optional[str]
    status: str
    error: Optional[str] = None

class ProcessSummary(BaseModel):
    total: int
    success: int
    failed: int

class ProcessFilesResponse(BaseModel):
    success: bool
    results: Optional[List[ProcessResult]] = None
    summary: Optional[ProcessSummary] = None
    error: Optional[str] = None

class ConnectionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None

class PDFWatermarkProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='pdf_watermark_')
        
    def __del__(self):
        # Cleanup temp directory
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def scan_pdf_files(self, path):
        """Recursively scan for PDF files in a directory"""
        pdf_files = []
        path = Path(path)
        
        if path.is_file() and path.suffix.lower() == '.pdf':
            return [path]
        elif path.is_dir():
            for file_path in path.rglob('*.pdf'):
                if file_path.is_file():
                    pdf_files.append(file_path)
        
        return pdf_files
    
    def sort_files(self, files, sort_type='filename'):
        """Sort files by filename or modification time"""
        if sort_type == 'filename':
            return sorted(files, key=lambda x: x.name.lower())
        elif sort_type == 'mtime':
            return sorted(files, key=lambda x: x.stat().st_mtime)
        return files
    
    def generate_filename(self, pattern, index, file_path, total_files):
        """Generate filename based on pattern with variables"""
        result = pattern
        current_time = datetime.now()
        
        # Handle {n} patterns for numbering
        n_patterns = re.findall(r'\{(n+)\}', pattern)
        for n_pattern in n_patterns:
            width = len(n_pattern)
            number = str(index).zfill(width)
            result = result.replace(f'{{{n_pattern}}}', number)
        
        # Handle datetime patterns
        datetime_patterns = re.findall(r'\{([^}]*[yMdHms][^}]*)\}', result)
        for dt_pattern in datetime_patterns:
            try:
                # Convert common datetime patterns
                dt_format = dt_pattern
                dt_format = dt_format.replace('yyyy', '%Y')
                dt_format = dt_format.replace('yy', '%y')
                dt_format = dt_format.replace('MM', '%m')
                dt_format = dt_format.replace('dd', '%d')
                dt_format = dt_format.replace('HH', '%H')
                dt_format = dt_format.replace('mm', '%M')
                dt_format = dt_format.replace('ss', '%S')
                
                formatted_date = current_time.strftime(dt_format)
                result = result.replace(f'{{{dt_pattern}}}', formatted_date)
            except:
                # If datetime formatting fails, keep original
                pass
        
        # Add .pdf extension if not present
        if not result.lower().endswith('.pdf'):
            result += '.pdf'
            
        return result
    
    def add_watermark(self, file_path, watermark_config):
        """Add watermark to PDF using Stirling PDF API"""
        try:
            with open(file_path, 'rb') as f:
                files = {'fileInput': f}
                
                data = {
                    'watermarkType': 'text',
                    'watermarkText': watermark_config['text'],
                    'fontSize': watermark_config['fontSize'],
                    'rotation': watermark_config['rotation'],
                    'opacity': watermark_config['opacity'] / 100.0,  # Convert percentage to decimal
                    'widthSpacer': watermark_config['widthSpacer'],
                    'heightSpacer': watermark_config['heightSpacer'],
                    'customColor': watermark_config['color'],
                    'convertPDFToImage': False
                }
                
                response = requests.post(WATERMARK_ENDPOINT, files=files, data=data, timeout=60)
                
                if response.status_code == 200:
                    # Save watermarked PDF to temp file
                    temp_file = os.path.join(self.temp_dir, f"watermarked_{os.path.basename(file_path)}")
                    with open(temp_file, 'wb') as temp_f:
                        temp_f.write(response.content)
                    return temp_file
                else:
                    raise Exception(f"API returned status code: {response.status_code}")
                    
        except Exception as e:
            raise Exception(f"Failed to add watermark: {str(e)}")
    
    def process_batch(self, files, watermark_config, naming_pattern, sort_type, output_dir):
        """Process batch of PDF files"""
        results = []
        sorted_files = self.sort_files(files, sort_type)
        total_files = len(sorted_files)
        
        # Check if naming pattern has {n} variable
        has_numbering = '{n' in naming_pattern
        
        for i, file_path in enumerate(sorted_files, 1):
            try:
                # Generate output filename
                if has_numbering or total_files == 1:
                    output_name = self.generate_filename(naming_pattern, i, file_path, total_files)
                else:
                    # Auto-append numbering if multiple files and no {n} in pattern
                    base_pattern = naming_pattern
                    if not base_pattern.lower().endswith('.pdf'):
                        base_pattern += '.pdf'
                    name_without_ext = base_pattern[:-4]
                    output_name = f"{name_without_ext}_{i:02d}.pdf"
                
                # Add watermark
                watermarked_file = self.add_watermark(file_path, watermark_config)
                
                # Move to output directory with new name
                output_path = os.path.join(output_dir, output_name)
                
                # Handle duplicate filenames
                counter = 1
                original_output_path = output_path
                while os.path.exists(output_path):
                    name_without_ext = original_output_path[:-4]
                    output_path = f"{name_without_ext}_({counter}).pdf"
                    counter += 1
                
                shutil.move(watermarked_file, output_path)
                
                results.append({
                    'original': str(file_path),
                    'output': output_path,
                    'status': 'success'
                })
                
            except Exception as e:
                results.append({
                    'original': str(file_path),
                    'output': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results

@app.get("/")
async def index():
    """Serve the main HTML page"""
    return FileResponse('static/index.html')

@app.post("/api/scan_files", response_model=ScanFilesResponse)
async def scan_files(request: ScanFilesRequest):
    """Scan for PDF files in selected paths"""
    try:
        processor = PDFWatermarkProcessor()
        all_files = []
        
        for path in request.paths:
            if os.path.exists(path):
                files = processor.scan_pdf_files(path)
                all_files.extend([str(f) for f in files])
        
        return ScanFilesResponse(
            success=True,
            files=all_files,
            count=len(all_files)
        )
        
    except Exception as e:
        return ScanFilesResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/preview_naming", response_model=PreviewNamingResponse)
async def preview_naming(request: PreviewNamingRequest):
    """Preview filename generation"""
    try:
        processor = PDFWatermarkProcessor()
        file_paths = [Path(f) for f in request.files]
        sorted_files = processor.sort_files(file_paths, request.sortType)
        
        previews = []
        total_files = len(sorted_files)
        has_numbering = '{n' in request.pattern
        
        for i, file_path in enumerate(sorted_files[:10], 1):  # Preview first 10 files
            if has_numbering or total_files == 1:
                output_name = processor.generate_filename(request.pattern, i, file_path, total_files)
            else:
                base_pattern = request.pattern
                if not base_pattern.lower().endswith('.pdf'):
                    base_pattern += '.pdf'
                name_without_ext = base_pattern[:-4]
                output_name = f"{name_without_ext}_{i:02d}.pdf"
            
            previews.append(PreviewItem(
                original=file_path.name,
                output=output_name
            ))
        
        return PreviewNamingResponse(
            success=True,
            previews=previews,
            total=total_files
        )
        
    except Exception as e:
        return PreviewNamingResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/process", response_model=ProcessFilesResponse)
async def process_files(request: ProcessFilesRequest):
    """Process PDF files with watermark"""
    try:
        if not request.files:
            raise HTTPException(status_code=400, detail="没有选择文件")
        
        if not request.watermark.text:
            raise HTTPException(status_code=400, detail="请输入水印文字")
        
        if not request.outputDir:
            raise HTTPException(status_code=400, detail="请选择输出目录")
        
        # Create output directory if it doesn't exist
        os.makedirs(request.outputDir, exist_ok=True)
        
        processor = PDFWatermarkProcessor()
        file_paths = []
        
        # Validate and convert file paths
        for file_path in request.files:
            path_obj = Path(file_path)
            if not path_obj.exists():
                raise HTTPException(status_code=400, detail=f"文件不存在: {file_path}")
            if not path_obj.suffix.lower() == '.pdf':
                raise HTTPException(status_code=400, detail=f"不是PDF文件: {file_path}")
            file_paths.append(path_obj)
        
        # Convert watermark config to dict for compatibility
        watermark_config = {
            'text': request.watermark.text,
            'fontSize': request.watermark.fontSize,
            'rotation': request.watermark.rotation,
            'opacity': request.watermark.opacity,
            'color': request.watermark.color,
            'widthSpacer': request.watermark.widthSpacer,
            'heightSpacer': request.watermark.heightSpacer
        }
        
        results = processor.process_batch(
            file_paths, 
            watermark_config, 
            request.namingPattern, 
            request.sortType, 
            request.outputDir
        )
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        # Convert results to Pydantic models
        process_results = [
            ProcessResult(
                original=r['original'],
                output=r.get('output'),
                status=r['status'],
                error=r.get('error')
            ) for r in results
        ]
        
        summary = ProcessSummary(
            total=len(results),
            success=success_count,
            failed=len(results) - success_count
        )
        
        return ProcessFilesResponse(
            success=True,
            results=process_results,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ProcessFilesResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/upload_files")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files and return their temporary paths"""
    try:
        uploaded_files = []
        
        for file in files:
            if not file.filename or not file.filename.lower().endswith('.pdf'):
                continue
                
            # Save uploaded file to temp directory
            temp_filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
            
            with open(temp_path, 'wb') as temp_file:
                content = await file.read()
                temp_file.write(content)
            
            uploaded_files.append(temp_path)
        
        return {
            "success": True,
            "files": uploaded_files,
            "count": len(uploaded_files)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/test_connection", response_model=ConnectionResponse)
async def test_connection():
    """Test connection to Stirling PDF API"""
    try:
        response = requests.get(f"{STIRLING_API_BASE}/api/v1/info/status", timeout=5)
        if response.status_code == 200:
            return ConnectionResponse(success=True, message='API连接正常')
        else:
            return ConnectionResponse(success=False, error=f'API返回状态码: {response.status_code}')
    except Exception as e:
        return ConnectionResponse(success=False, error=f'无法连接到API: {str(e)}')

if __name__ == '__main__':
    print("PDF水印批处理工具启动中...")
    print(f"请在浏览器中访问: http://localhost:8001")
    print(f"Stirling PDF API: {STIRLING_API_BASE}")
    uvicorn.run("make_screenplay_pdf:app", host="0.0.0.0", port=8001, reload=True)
