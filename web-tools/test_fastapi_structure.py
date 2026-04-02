#!/usr/bin/env python3
"""
Test script to verify the FastAPI PDF Watermark Tool structure
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Test if all required files exist for FastAPI version"""
    required_files = [
        'make_screenplay_pdf.py',
        'requirements.txt',
        'README.md',
        'static/index.html',
        'static/css/style.css',
        'static/js/script.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files exist")
        return True

def test_fastapi_content():
    """Test if main file contains FastAPI components"""
    tests = []
    
    try:
        with open('make_screenplay_pdf.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check FastAPI imports
        if 'from fastapi import FastAPI' in content:
            tests.append(("FastAPI Import", True, "FastAPI imported correctly"))
        else:
            tests.append(("FastAPI Import", False, "FastAPI import not found"))
        
        # Check Pydantic models
        if 'from pydantic import BaseModel' in content:
            tests.append(("Pydantic Models", True, "Pydantic BaseModel imported"))
        else:
            tests.append(("Pydantic Models", False, "Pydantic import not found"))
        
        # Check uvicorn
        if 'import uvicorn' in content:
            tests.append(("Uvicorn Server", True, "Uvicorn imported"))
        else:
            tests.append(("Uvicorn Server", False, "Uvicorn import not found"))
        
        # Check API routes
        routes = ['@app.get("/")', '@app.post("/api/scan_files")', '@app.post("/api/process")']
        found_routes = sum(1 for route in routes if route in content)
        if found_routes >= 2:
            tests.append(("API Routes", True, f"Found {found_routes}/3 main routes"))
        else:
            tests.append(("API Routes", False, f"Only found {found_routes}/3 routes"))
        
        # Check static files mount
        if 'StaticFiles' in content and 'app.mount' in content:
            tests.append(("Static Files", True, "Static files mounted"))
        else:
            tests.append(("Static Files", False, "Static files not properly mounted"))
        
    except Exception as e:
        tests.append(("File Reading", False, f"Error reading file: {e}"))
    
    print("\n📋 FastAPI Content Tests:")
    all_passed = True
    for test_name, passed, message in tests:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}: {message}")
        if not passed:
            all_passed = False
    
    return all_passed

def test_static_files():
    """Test static files configuration"""
    tests = []
    
    # Check HTML file
    try:
        with open('static/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        if '/static/css/style.css' in html_content:
            tests.append(("HTML CSS Link", True, "CSS linked correctly"))
        else:
            tests.append(("HTML CSS Link", False, "CSS link not found or incorrect"))
        
        if '/static/js/script.js' in html_content:
            tests.append(("HTML JS Link", True, "JavaScript linked correctly"))
        else:
            tests.append(("HTML JS Link", False, "JavaScript link not found or incorrect"))
        
        if '{{ url_for(' not in html_content:
            tests.append(("Template Syntax", True, "No Flask template syntax found"))
        else:
            tests.append(("Template Syntax", False, "Flask template syntax still present"))
            
    except Exception as e:
        tests.append(("HTML File", False, f"Error reading HTML: {e}"))
    
    print("\n🌐 Static Files Tests:")
    all_passed = True
    for test_name, passed, message in tests:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}: {message}")
        if not passed:
            all_passed = False
    
    return all_passed

def test_requirements():
    """Test requirements.txt for FastAPI dependencies"""
    tests = []
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.read()
        
        required_packages = ['fastapi', 'uvicorn', 'pydantic', 'requests']
        for package in required_packages:
            if package in requirements.lower():
                tests.append((f"{package.title()}", True, f"{package} dependency found"))
            else:
                tests.append((f"{package.title()}", False, f"{package} dependency missing"))
        
        # Check if Flask is removed
        if 'flask' not in requirements.lower():
            tests.append(("Flask Removal", True, "Flask dependency removed"))
        else:
            tests.append(("Flask Removal", False, "Flask dependency still present"))
            
    except Exception as e:
        tests.append(("Requirements File", False, f"Error reading requirements: {e}"))
    
    print("\n📦 Dependencies Tests:")
    all_passed = True
    for test_name, passed, message in tests:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}: {message}")
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    print("🧪 PDF水印批处理工具 - FastAPI重构验证")
    print("=" * 60)
    
    structure_ok = test_project_structure()
    fastapi_ok = test_fastapi_content()
    static_ok = test_static_files()
    requirements_ok = test_requirements()
    
    print("\n" + "=" * 60)
    if structure_ok and fastapi_ok and static_ok and requirements_ok:
        print("🎉 FastAPI重构完成！所有测试通过。")
        print("\n📝 启动步骤:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动应用: python make_screenplay_pdf.py")
        print("3. 访问地址: http://localhost:8000")
        print("4. API文档: http://localhost:8000/docs")
        print("\n🚀 主要改进:")
        print("- ⚡ FastAPI异步处理，性能更优")
        print("- 📚 自动生成API文档")
        print("- 🔧 Pydantic数据验证")
        print("- 🎯 前后端完全分离")
        return True
    else:
        print("❌ 部分测试失败，请检查重构结果。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
