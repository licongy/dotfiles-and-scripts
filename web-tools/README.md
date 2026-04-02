# PDF水印批处理工具

一个基于FastAPI的Web应用程序，用于批量为PDF文件添加水印、重命名并保存到指定目录。

## 功能特性

- 🔍 **文件选择**: 支持单个PDF文件、多个文件或整个文件夹
- 📝 **智能命名**: 支持自定义命名规则，包括自动编号和日期时间变量
- 🔤 **文件排序**: 按文件名或修改时间排序
- 💧 **水印设置**: 完全可定制的文本水印（文字、角度、大小、透明度、颜色、间距）
- 📁 **批量处理**: 一键批量处理多个PDF文件
- 📊 **实时反馈**: 处理进度显示和详细结果报告

## 系统要求

- Python 3.7+
- FastAPI 0.104.1+
- uvicorn 0.24.0+
- requests 2.31.0+
- Stirling PDF API服务 (http://192.168.8.88:18080)

## 安装步骤

1. **克隆或下载项目文件**
   ```bash
   # 确保所有文件都在同一目录下
   make_screenplay_pdf.py
   requirements.txt
   templates/index.html
   static/css/style.css
   static/js/script.js
   ```

2. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   python make_screenplay_pdf.py
   ```

4. **访问Web界面**
   - 打开浏览器访问: http://localhost:8000
   - 工具会自动测试与Stirling PDF API的连接
   - 可访问 http://localhost:8000/docs 查看自动生成的API文档

## 使用说明

### 1. 选择PDF文件
- **单个文件**: 输入完整文件路径，如 `/path/to/document.pdf`
- **多个文件**: 用分号分隔多个文件路径，如 `/path/to/file1.pdf;/path/to/file2.pdf`
- **文件夹**: 输入文件夹路径，工具会自动扫描所有PDF文件

### 2. 设置文件排序
- **按原文件名排序** (默认): 按文件名字母顺序
- **按更新时间排序**: 按文件修改时间顺序

### 3. 配置命名规则
支持以下变量:
- `{n}`, `{nn}`, `{nnn}` 等: 自动编号，n的数量表示最小位数
- `{yyyy}`: 四位年份
- `{MM}`: 两位月份
- `{dd}`: 两位日期
- `{HH}`: 两位小时
- `{mm}`: 两位分钟
- `{ss}`: 两位秒钟

**示例**:
- `《权力的游戏》剧本S01E{nn}-{yyyyMMdd}` → `《权力的游戏》剧本S01E01-20250103`
- `文档{nnn}` → `文档001`, `文档002`, `文档003`

### 4. 水印设置
- **水印文字**: 必填，显示在PDF上的文字
- **旋转角度**: 0-360度，默认45度
- **字体大小**: 8-200，默认48
- **不透明度**: 1-100%，默认10%
- **字体颜色**: 颜色选择器，默认灰色
- **水平/垂直间距**: 控制水印重复的间距

### 5. 选择输出目录
输入保存处理后文件的目录路径

### 6. 开始处理
点击"开始处理"按钮，工具会:
1. 按设定顺序处理每个PDF文件
2. 调用Stirling PDF API添加水印
3. 按命名规则重命名文件
4. 保存到指定输出目录
5. 显示处理结果报告

## API配置

工具默认连接到 `http://192.168.8.88:18080` 的Stirling PDF API。

如需修改API地址，请编辑 `make_screenplay_pdf.py` 文件中的 `STIRLING_API_BASE` 变量。

## 故障排除

### 连接问题
- 确保Stirling PDF API服务正在运行
- 检查网络连接和防火墙设置
- 验证API地址是否正确

### 文件路径问题
- 使用完整的绝对路径
- 确保路径中的文件确实存在
- 检查文件权限

### 处理失败
- 检查PDF文件是否损坏
- 确保输出目录有写入权限
- 查看错误信息获取详细原因

## 技术架构

- **后端**: FastAPI (Python) + Pydantic数据验证
- **前端**: Bootstrap 5 + 原生JavaScript (前后端分离)
- **API集成**: Stirling PDF REST API
- **文件处理**: Python pathlib + requests
- **服务器**: Uvicorn ASGI服务器

## 开发说明

项目结构:
```
├── make_screenplay_pdf.py    # 主FastAPI应用文件
├── requirements.txt          # Python依赖
├── static/
│   ├── index.html           # 主页面 (纯静态)
│   ├── css/style.css        # 样式文件
│   └── js/script.js         # 前端JavaScript
└── temp/                    # 临时文件目录
```

### API端点
- `GET /` - 主页面
- `POST /api/scan_files` - 扫描PDF文件
- `POST /api/preview_naming` - 预览文件命名
- `POST /api/process` - 批量处理文件
- `GET /api/test_connection` - 测试API连接
- `GET /docs` - 自动生成的API文档 (Swagger UI)

## 许可证

本项目仅供学习和内部使用。

## 更新日志

### v2.0.0 (2025-01-03)
- 🚀 **重大重构**: 从Flask迁移到FastAPI
- ⚡ **性能提升**: 异步处理，更快的响应速度
- 📚 **自动文档**: 内置Swagger UI API文档
- 🔧 **类型安全**: Pydantic数据验证和类型提示
- 🎯 **前后端分离**: 纯API后端 + 静态前端
- 📦 **轻量部署**: 更小的依赖包，更快的启动

### v1.0.0 (2025-01-03)
- 初始版本发布 (Flask版本)
- 支持批量PDF水印处理
- 智能文件命名系统
- Web界面操作
- Stirling PDF API集成
