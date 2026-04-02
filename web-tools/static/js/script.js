// PDF Watermark Tool - Frontend JavaScript

class PDFWatermarkTool {
    constructor() {
        this.selectedFiles = [];
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateOpacityDisplay();
        this.testConnectionOnLoad();
    }

    bindEvents() {
        // Connection test
        document.getElementById('testConnection').addEventListener('click', () => this.testConnection());

        // File operations
        document.getElementById('scanFiles').addEventListener('click', () => this.scanFiles());
        document.getElementById('browseFiles').addEventListener('click', () => this.browseFiles());
        document.getElementById('browseFolders').addEventListener('click', () => this.browseFolders());
        document.getElementById('browseOutput').addEventListener('click', () => this.browseOutput());

        // File input change events
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileSelection(e));
        document.getElementById('folderInput').addEventListener('change', (e) => this.handleFolderSelection(e));
        document.getElementById('outputFolderInput').addEventListener('change', (e) => this.handleOutputFolderSelection(e));

        // Naming preview
        document.getElementById('previewNaming').addEventListener('click', () => this.previewNaming());
        document.getElementById('namingPattern').addEventListener('input', () => this.autoPreviewNaming());

        // Watermark settings
        document.getElementById('opacity').addEventListener('input', () => this.updateOpacityDisplay());

        // Process files
        document.getElementById('processFiles').addEventListener('click', () => this.processFiles());

        // Form validation
        document.getElementById('watermarkText').addEventListener('input', () => this.validateForm());
        document.getElementById('outputDir').addEventListener('input', () => this.validateForm());

        // Sort type change
        document.querySelectorAll('input[name="sortType"]').forEach(radio => {
            radio.addEventListener('change', () => this.autoPreviewNaming());
        });

        // File path enter key
        document.getElementById('filePath').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.scanFiles();
            }
        });
    }

    async testConnection() {
        const button = document.getElementById('testConnection');
        const status = document.getElementById('connectionStatus');
        
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-arrow-clockwise spinner-border spinner-border-sm"></i> 测试中...';
        status.innerHTML = '<span class="badge connection-testing">测试中...</span>';

        try {
            const response = await fetch('/api/test_connection');
            const data = await response.json();

            if (data.success) {
                status.innerHTML = '<span class="badge connection-success">连接正常</span>';
                this.showAlert('success', 'API连接测试成功！');
            } else {
                status.innerHTML = '<span class="badge connection-error">连接失败</span>';
                this.showAlert('danger', `连接失败: ${data.error}`);
            }
        } catch (error) {
            status.innerHTML = '<span class="badge connection-error">连接失败</span>';
            this.showAlert('danger', `连接测试失败: ${error.message}`);
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-arrow-clockwise"></i> 测试连接';
        }
    }

    async testConnectionOnLoad() {
        // Auto test connection when page loads
        setTimeout(() => this.testConnection(), 1000);
    }

    browseFiles() {
        // Trigger file input for PDF files
        document.getElementById('fileInput').click();
    }

    browseFolders() {
        // Trigger folder input
        document.getElementById('folderInput').click();
    }

    browseOutput() {
        // Trigger folder input for output directory
        document.getElementById('outputFolderInput').click();
    }

    async handleFileSelection(event) {
        const files = Array.from(event.target.files);
        if (files.length === 0) return;

        // Filter PDF files
        const pdfFiles = files.filter(file => file.name.toLowerCase().endsWith('.pdf'));
        if (pdfFiles.length === 0) {
            this.showAlert('warning', '请选择PDF文件');
            return;
        }

        // Upload files to server
        try {
            const formData = new FormData();
            pdfFiles.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch('/api/upload_files', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.selectedFiles = data.files;
                this.selectedFileObjects = pdfFiles;

                // Update the input field to show selected files
                const filePathInput = document.getElementById('filePath');
                if (pdfFiles.length === 1) {
                    filePathInput.value = pdfFiles[0].name;
                } else {
                    filePathInput.value = `已选择 ${pdfFiles.length} 个PDF文件`;
                }

                this.displayFiles();
                this.validateForm();
                this.showAlert('success', `已上传 ${data.count} 个PDF文件`);
            } else {
                this.showAlert('danger', `文件上传失败: ${data.error}`);
            }
        } catch (error) {
            this.showAlert('danger', `文件上传失败: ${error.message}`);
        }
    }

    async handleFolderSelection(event) {
        const files = Array.from(event.target.files);
        if (files.length === 0) return;

        // Filter only PDF files
        const pdfFiles = files.filter(file => file.name.toLowerCase().endsWith('.pdf'));
        
        if (pdfFiles.length === 0) {
            this.showAlert('warning', '所选文件夹中没有找到PDF文件');
            return;
        }

        // Upload files to server
        try {
            const formData = new FormData();
            pdfFiles.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch('/api/upload_files', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.selectedFiles = data.files;
                this.selectedFileObjects = pdfFiles;

                // Update the input field
                const filePathInput = document.getElementById('filePath');
                filePathInput.value = `已选择文件夹，包含 ${data.count} 个PDF文件`;

                this.displayFiles();
                this.validateForm();
                this.showAlert('success', `从文件夹中上传了 ${data.count} 个PDF文件`);
            } else {
                this.showAlert('danger', `文件上传失败: ${data.error}`);
            }
        } catch (error) {
            this.showAlert('danger', `文件上传失败: ${error.message}`);
        }
    }

    handleOutputFolderSelection(event) {
        const files = Array.from(event.target.files);
        if (files.length === 0) return;

        // Get the folder path from the first file
        const firstFile = files[0];
        let folderPath = '';
        
        if (firstFile.webkitRelativePath) {
            // Extract folder path from webkitRelativePath
            const pathParts = firstFile.webkitRelativePath.split('/');
            pathParts.pop(); // Remove filename
            folderPath = pathParts.join('/');
        } else {
            folderPath = '已选择的文件夹';
        }

        // Update the output directory input
        document.getElementById('outputDir').value = folderPath;
        this.validateForm();
        this.showAlert('success', '已选择输出目录');
    }

    async scanFiles() {
        const filePath = document.getElementById('filePath').value.trim();
        if (!filePath) {
            this.showAlert('warning', '请输入文件或文件夹路径');
            return;
        }

        const button = document.getElementById('scanFiles');
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-search spinner-border spinner-border-sm"></i> 扫描中...';

        try {
            // Split paths by semicolon for multiple files
            const paths = filePath.split(';').map(p => p.trim()).filter(p => p);
            
            const response = await fetch('/api/scan_files', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ paths: paths })
            });

            const data = await response.json();

            if (data.success) {
                this.selectedFiles = data.files;
                this.displayFiles();
                this.showAlert('success', `成功找到 ${data.count} 个PDF文件`);
                this.validateForm();
            } else {
                this.showAlert('danger', `扫描失败: ${data.error}`);
            }
        } catch (error) {
            this.showAlert('danger', `扫描失败: ${error.message}`);
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-search"></i> 扫描';
        }
    }

    displayFiles() {
        const fileList = document.getElementById('fileList');
        const fileCount = document.getElementById('fileCount');
        const fileItems = document.getElementById('fileItems');

        if (this.selectedFiles.length === 0) {
            fileList.style.display = 'none';
            return;
        }

        fileCount.textContent = this.selectedFiles.length;
        fileItems.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const fileName = file.split('/').pop();
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div>
                    <div class="file-name">${fileName}</div>
                    <div class="file-path">${file}</div>
                </div>
                <i class="bi bi-x-circle file-remove" onclick="pdfTool.removeFile(${index})"></i>
            `;
            fileItems.appendChild(fileItem);
        });

        fileList.style.display = 'block';
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.displayFiles();
        this.validateForm();
        
        // Clear preview if no files left
        if (this.selectedFiles.length === 0) {
            document.getElementById('namingPreview').style.display = 'none';
        }
    }

    async previewNaming() {
        if (this.selectedFiles.length === 0) {
            this.showAlert('warning', '请先选择PDF文件');
            return;
        }

        const pattern = document.getElementById('namingPattern').value.trim();
        if (!pattern) {
            this.showAlert('warning', '请输入命名模式');
            return;
        }

        const sortType = document.querySelector('input[name="sortType"]:checked').value;

        try {
            const response = await fetch('/api/preview_naming', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pattern: pattern,
                    files: this.selectedFiles,
                    sortType: sortType
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayNamingPreview(data.previews, data.total);
            } else {
                this.showAlert('danger', `预览失败: ${data.error}`);
            }
        } catch (error) {
            this.showAlert('danger', `预览失败: ${error.message}`);
        }
    }

    autoPreviewNaming() {
        // Auto preview when pattern changes (debounced)
        clearTimeout(this.previewTimeout);
        this.previewTimeout = setTimeout(() => {
            if (this.selectedFiles.length > 0 && document.getElementById('namingPattern').value.trim()) {
                this.previewNaming();
            }
        }, 500);
    }

    displayNamingPreview(previews, total) {
        const previewContainer = document.getElementById('namingPreview');
        const previewItems = document.getElementById('previewItems');

        previewItems.innerHTML = '';

        previews.forEach(preview => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <div class="preview-original">${preview.original}</div>
                <div class="preview-arrow">→</div>
                <div class="preview-output">${preview.output}</div>
            `;
            previewItems.appendChild(previewItem);
        });

        if (total > previews.length) {
            const moreItem = document.createElement('div');
            moreItem.className = 'preview-item';
            moreItem.innerHTML = `
                <div class="text-muted text-center w-100">
                    ... 还有 ${total - previews.length} 个文件
                </div>
            `;
            previewItems.appendChild(moreItem);
        }

        previewContainer.style.display = 'block';
    }

    updateOpacityDisplay() {
        const opacity = document.getElementById('opacity').value;
        document.getElementById('opacityValue').textContent = `${opacity}%`;
    }

    validateForm() {
        const hasFiles = this.selectedFiles.length > 0;
        const hasWatermarkText = document.getElementById('watermarkText').value.trim() !== '';
        const hasOutputDir = document.getElementById('outputDir').value.trim() !== '';

        const processButton = document.getElementById('processFiles');
        processButton.disabled = !hasFiles || !hasWatermarkText || !hasOutputDir || this.isProcessing;
    }

    async processFiles() {
        if (this.isProcessing) return;

        const watermarkText = document.getElementById('watermarkText').value.trim();
        const outputDir = document.getElementById('outputDir').value.trim();
        const namingPattern = document.getElementById('namingPattern').value.trim() || '{n}';

        if (!watermarkText) {
            this.showAlert('warning', '请输入水印文字');
            return;
        }

        if (!outputDir) {
            this.showAlert('warning', '请选择输出目录');
            return;
        }

        this.isProcessing = true;
        this.showProgress(true);
        this.updateProgressBar(0, '准备处理...');

        const watermarkConfig = {
            text: watermarkText,
            fontSize: parseInt(document.getElementById('fontSize').value),
            rotation: parseInt(document.getElementById('rotation').value),
            opacity: parseInt(document.getElementById('opacity').value),
            color: document.getElementById('watermarkColor').value,
            widthSpacer: parseInt(document.getElementById('widthSpacer').value),
            heightSpacer: parseInt(document.getElementById('heightSpacer').value)
        };

        const sortType = document.querySelector('input[name="sortType"]:checked').value;

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    files: this.selectedFiles,
                    watermark: watermarkConfig,
                    namingPattern: namingPattern,
                    sortType: sortType,
                    outputDir: outputDir
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data.results, data.summary);
                this.showAlert('success', `处理完成！成功处理 ${data.summary.success} 个文件，失败 ${data.summary.failed} 个文件。`);
            } else {
                this.showAlert('danger', `处理失败: ${data.error}`);
            }
        } catch (error) {
            this.showAlert('danger', `处理失败: ${error.message}`);
        } finally {
            this.isProcessing = false;
            this.showProgress(false);
            this.validateForm();
        }
    }

    showProgress(show) {
        const container = document.getElementById('progressContainer');
        const button = document.getElementById('processFiles');

        if (show) {
            container.style.display = 'block';
            button.innerHTML = '<i class="bi bi-hourglass-split"></i> 处理中...';
            button.disabled = true;
        } else {
            container.style.display = 'none';
            button.innerHTML = '<i class="bi bi-play-circle"></i> 开始处理';
        }
    }

    updateProgressBar(percent, text) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        progressBar.style.width = `${percent}%`;
        progressText.textContent = text;
    }

    displayResults(results, summary) {
        const container = document.getElementById('resultsContainer');
        const summaryDiv = document.getElementById('resultsSummary');
        const tableBody = document.getElementById('resultsTableBody');

        // Display summary
        summaryDiv.innerHTML = `
            <strong>处理完成！</strong><br>
            总计: ${summary.total} 个文件 | 
            成功: <span class="text-success">${summary.success}</span> | 
            失败: <span class="text-danger">${summary.failed}</span>
        `;

        // Display detailed results
        tableBody.innerHTML = '';
        results.forEach(result => {
            const row = document.createElement('tr');
            const fileName = result.original.split('/').pop();
            const outputName = result.output ? result.output.split('/').pop() : '-';
            
            let statusBadge;
            if (result.status === 'success') {
                statusBadge = '<span class="badge status-success">成功</span>';
            } else {
                statusBadge = `<span class="badge status-error" title="${result.error}">失败</span>`;
            }

            row.innerHTML = `
                <td>${fileName}</td>
                <td>${outputName}</td>
                <td>${statusBadge}</td>
            `;
            tableBody.appendChild(row);
        });

        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });
    }

    showAlert(type, message) {
        // Remove existing floating alerts
        const existingAlerts = document.querySelectorAll('.alert-floating');
        existingAlerts.forEach(alert => {
            alert.classList.add('fade-out');
            setTimeout(() => alert.remove(), 300);
        });

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible alert-floating fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Append to body for floating effect
        document.body.appendChild(alertDiv);

        // Auto dismiss after 5 seconds for success/info alerts
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.classList.add('fade-out');
                    setTimeout(() => alertDiv.remove(), 300);
                }
            }, 5000);
        }

        // Manual close button
        const closeBtn = alertDiv.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alertDiv.classList.add('fade-out');
                setTimeout(() => alertDiv.remove(), 300);
            });
        }
    }
}

// Initialize the tool when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.pdfTool = new PDFWatermarkTool();
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// Handle page unload
window.addEventListener('beforeunload', function(e) {
    if (window.pdfTool && window.pdfTool.isProcessing) {
        e.preventDefault();
        e.returnValue = '正在处理文件，确定要离开吗？';
        return e.returnValue;
    }
});
