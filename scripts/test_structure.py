#!/usr/bin/env python3
"""
Test script to verify the PDF Watermark Tool structure
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Test if all required files exist"""
    required_files = [
        'make_screenplay_pdf.py',
        'requirements.txt',
        'README.md',
        'templates/index.html',
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

def test_file_contents():
    """Test if key files have content"""
    tests = []
    
    # Test main Python file
    try:
        with open('make_screenplay_pdf.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Flask' in content and 'PDFWatermarkProcessor' in content:
                tests.append(("make_screenplay_pdf.py", True, "Contains Flask app and processor class"))
            else:
                tests.append(("make_screenplay_pdf.py", False, "Missing key components"))
    except Exception as e:
        tests.append(("make_screenplay_pdf.py", False, f"Error reading file: {e}"))
    
    # Test HTML template
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'PDF水印批处理工具' in content and 'watermarkText' in content:
                tests.append(("templates/index.html", True, "Contains UI elements"))
            else:
                tests.append(("templates/index.html", False, "Missing key UI elements"))
    except Exception as e:
        tests.append(("templates/index.html", False, f"Error reading file: {e}"))
    
    # Test CSS
    try:
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            content = f.read()
            if '.file-item' in content and '.watermark' in content or 'body' in content:
                tests.append(("static/css/style.css", True, "Contains styling rules"))
            else:
                tests.append(("static/css/style.css", False, "Missing key styles"))
    except Exception as e:
        tests.append(("static/css/style.css", False, f"Error reading file: {e}"))
    
    # Test JavaScript
    try:
        with open('static/js/script.js', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'PDFWatermarkTool' in content and 'testConnection' in content:
                tests.append(("static/js/script.js", True, "Contains main class and functions"))
            else:
                tests.append(("static/js/script.js", False, "Missing key functions"))
    except Exception as e:
        tests.append(("static/js/script.js", False, f"Error reading file: {e}"))
    
    print("\n📋 File Content Tests:")
    all_passed = True
    for filename, passed, message in tests:
        status = "✅" if passed else "❌"
        print(f"   {status} {filename}: {message}")
        if not passed:
            all_passed = False
    
    return all_passed

def test_configuration():
    """Test configuration values"""
    try:
        with open('make_screenplay_pdf.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        tests = []
        
        # Check API endpoint
        if 'http://192.168.8.88:18080' in content:
            tests.append(("API Endpoint", True, "Stirling PDF API configured"))
        else:
            tests.append(("API Endpoint", False, "API endpoint not found"))
        
        # Check Flask configuration
        if "app = Flask(__name__)" in content:
            tests.append(("Flask App", True, "Flask app initialized"))
        else:
            tests.append(("Flask App", False, "Flask app not found"))
        
        # Check routes
        routes = ['/', '/api/scan_files', '/api/preview_naming', '/api/process', '/api/test_connection']
        found_routes = sum(1 for route in routes if f"'{route}'" in content or f'"{route}"' in content)
        if found_routes >= 4:
            tests.append(("API Routes", True, f"Found {found_routes}/5 routes"))
        else:
            tests.append(("API Routes", False, f"Only found {found_routes}/5 routes"))
        
        print("\n⚙️  Configuration Tests:")
        all_passed = True
        for test_name, passed, message in tests:
            status = "✅" if passed else "❌"
            print(f"   {status} {test_name}: {message}")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        return False

def main():
    print("🧪 PDF水印批处理工具 - 结构测试")
    print("=" * 50)
    
    structure_ok = test_project_structure()
    content_ok = test_file_contents()
    config_ok = test_configuration()
    
    print("\n" + "=" * 50)
    if structure_ok and content_ok and config_ok:
        print("🎉 所有测试通过！项目结构完整，可以启动应用。")
        print("\n📝 启动步骤:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动应用: python make_screenplay_pdf.py")
        print("3. 访问地址: http://localhost:5000")
        return True
    else:
        print("❌ 部分测试失败，请检查项目文件。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
