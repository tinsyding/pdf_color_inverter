// 全局变量
let currentFile = null;
let selectedPages = [];
let processedFileUrl = null;

// DOM 元素
const uploadSection = document.getElementById('uploadSection');
const previewSection = document.getElementById('previewSection');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');
const uploadArea = document.getElementById('uploadArea');
const pdfFileInput = document.getElementById('pdfFile');
const previewGrid = document.getElementById('previewGrid');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultText = document.getElementById('resultText');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// 初始化事件监听器
function initializeEventListeners() {
    // 文件选择
    pdfFileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => pdfFileInput.click());
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
        uploadFile(file);
    } else {
        showError('请选择有效的PDF文件');
    }
}

// 处理拖拽悬停
function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

// 处理拖拽离开
function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

// 处理文件拖拽
function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            uploadFile(file);
        } else {
            showError('请选择有效的PDF文件');
        }
    }
}

// 上传文件
async function uploadFile(file) {
    try {
        showLoading('正在加载PDF，请稍候...');
        
        const formData = new FormData();
        formData.append('pdf', file);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('上传失败');
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentFile = file;
            showPreview(data.thumbnails, data.totalPages);
            updateStep(2);
        } else {
            throw new Error(data.error || '上传失败');
        }
        
    } catch (error) {
        showError('上传失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示预览
function showPreview(thumbnails, totalPages) {
    uploadSection.style.display = 'none';
    previewSection.style.display = 'block';
    
    // 清空预览网格
    previewGrid.innerHTML = '';
    
    // 创建页面卡片
    thumbnails.forEach((thumbnail, index) => {
        const pageCard = createPageCard(index, thumbnail);
        previewGrid.appendChild(pageCard);
    });
    
    // 默认全选
    selectAll();
    updateToggleSelectBtn();
}

// 创建页面卡片
function createPageCard(pageIndex, thumbnailUrl) {
    const card = document.createElement('div');
    card.className = 'page-card selected fade-in';
    card.dataset.pageIndex = pageIndex;
    
    card.innerHTML = `
        <img src="${thumbnailUrl}" alt="第 ${pageIndex + 1} 页" class="page-image">
        <div class="page-info">
            <div class="page-number">第 ${pageIndex + 1} 页</div>
            <div class="page-size">点击选择</div>
        </div>
    `;
    
    // 添加点击事件
    card.addEventListener('click', () => togglePageSelection(card, pageIndex));
    
    return card;
}

// 切换页面选择状态
function togglePageSelection(card, pageIndex) {
    const isSelected = card.classList.contains('selected');
    
    if (isSelected) {
        card.classList.remove('selected');
        selectedPages = selectedPages.filter(page => page !== pageIndex);
    } else {
        card.classList.add('selected');
        selectedPages.push(pageIndex);
    }
    
    updateProcessButton();
    updateToggleSelectBtn();
}

function toggleSelectAll() {
    const cards = document.querySelectorAll('.page-card');
    if (isAllSelected()) {
        deselectAll();
    } else {
        selectAll();
    }
}

function isAllSelected() {
    const cards = document.querySelectorAll('.page-card');
    return cards.length > 0 && selectedPages.length === cards.length;
}

function selectAll() {
    const cards = document.querySelectorAll('.page-card');
    selectedPages = [];
    cards.forEach((card, index) => {
        card.classList.add('selected');
        selectedPages.push(index);
    });
    updateProcessButton();
    updateToggleSelectBtn();
}

function deselectAll() {
    const cards = document.querySelectorAll('.page-card');
    cards.forEach(card => {
        card.classList.remove('selected');
    });
    selectedPages = [];
    updateProcessButton();
    updateToggleSelectBtn();
}

function updateToggleSelectBtn() {
    const btn = document.getElementById('toggleSelectBtn');
    if (!btn) return;
    btn.textContent = isAllSelected() ? '取消全选' : '全选';
}

// 更新处理按钮状态
function updateProcessButton() {
    const processBtn = document.getElementById('processBtn');
    if (selectedPages.length > 0) {
        processBtn.disabled = false;
        processBtn.innerHTML = `<i class="fas fa-magic"></i> 开始处理 (${selectedPages.length} 页)`;
    } else {
        processBtn.disabled = true;
        processBtn.innerHTML = `<i class="fas fa-magic"></i> 请选择页面`;
    }
}

// 处理PDF
async function processPDF() {
    if (selectedPages.length === 0) {
        showError('请至少选择一页进行处理');
        return;
    }
    
    try {
        showProgress();
        updateStep(3);
        
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                selectedPages: selectedPages
            })
        });
        
        if (!response.ok) {
            throw new Error('处理失败');
        }
        
        const data = await response.json();
        
        if (data.success) {
            processedFileUrl = data.downloadUrl;
            showResult(data.message);
        } else {
            throw new Error(data.error || '处理失败');
        }
        
    } catch (error) {
        showError('处理失败: ' + error.message);
        updateStep(2);
    }
}

// 显示进度
function showProgress() {
    previewSection.style.display = 'none';
    progressSection.style.display = 'block';
    
    // 模拟进度更新
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        updateProgress(progress, '正在处理PDF页面...');
        
        if (progress >= 90) {
            clearInterval(interval);
        }
    }, 500);
}

// 更新进度
function updateProgress(percentage, text) {
    progressFill.style.width = percentage + '%';
    if (text) {
        progressText.textContent = text;
    }
}

// 显示结果
function showResult(message) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    resultText.textContent = message || 'PDF已成功处理';
}

// 下载文件
function downloadFile() {
    if (processedFileUrl) {
        const link = document.createElement('a');
        link.href = processedFileUrl;
        link.download = 'processed_pdf.pdf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// 重置应用
function resetApp() {
    // 重置状态
    currentFile = null;
    selectedPages = [];
    processedFileUrl = null;
    
    // 重置UI
    uploadSection.style.display = 'block';
    previewSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    
    // 重置文件输入
    pdfFileInput.value = '';
    
    // 重置步骤
    updateStep(1);
}

// 更新步骤指示器
function updateStep(stepNumber) {
    // 移除所有活动状态
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    
    // 激活当前步骤
    document.getElementById(`step${stepNumber}`).classList.add('active');
}

// 显示加载状态
function showLoading(message = '加载中...') {
    const loading = document.getElementById('globalLoading');
    if (loading) {
        loading.style.display = 'flex';
        const text = loading.querySelector('div[style*="font-size"]');
        if (text) text.textContent = message;
    }
}

// 隐藏加载状态
function hideLoading() {
    const loading = document.getElementById('globalLoading');
    if (loading) loading.style.display = 'none';
}

// 显示错误
function showError(message) {
    alert('错误: ' + message);
}

// 显示成功消息
function showSuccess(message) {
    alert('成功: ' + message);
}

// 工具函数：格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 工具函数：防抖
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 工具函数：节流
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
} 