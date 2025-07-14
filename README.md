# PDF 页面反色工具 - Web版

一个现代化的Web应用，用于反转PDF页面的颜色，将白色背景变为黑色，黑色文字变为白色，适合夜间阅读。

**作者：tinsy**

---

## 功能特点

- 🎨 **现代化界面**：采用响应式设计，支持桌面和移动设备
- 📁 **拖拽上传**：支持拖拽PDF文件到页面进行上传
- 👀 **页面预览**：上传后自动生成每页缩略图，方便选择
- ✅ **多选页面**：支持选择多个页面进行反色处理
- ⚡ **实时处理**：显示处理进度，完成后自动提供下载链接
- 📱 **移动友好**：完全响应式设计，在手机上也能完美使用
- 🧹 **一键清理缓存**：支持清理临时文件和缩略图

## 技术栈

- **后端**：Flask (Python)
- **前端**：HTML5 + CSS3 + JavaScript
- **PDF处理**：PyMuPDF (fitz)
- **图像处理**：Pillow (PIL)

## 安装和运行

### 1. 安装依赖（源码运行）

```bash
pip install -r requirements.txt
```

### 2. 运行应用（源码）

```bash
python run.py
```

### 3. 访问应用

打开浏览器访问：`http://localhost:4999`

---

## 使用说明

### 步骤1：选择PDF文件
- 点击"选择文件"按钮选择PDF文件
- 或者直接将PDF文件拖拽到上传区域

### 步骤2：选择要反色的页面
- 上传成功后，会显示所有页面的缩略图
- 点击页面卡片来选择或取消选择
- 使用"全选"和"取消全选"按钮快速操作
- 如需更换PDF，点击“重新选择PDF”按钮

### 步骤3：开始处理
- 点击"开始处理"按钮
- 等待处理完成
- 下载处理后的PDF文件

### 步骤4：清理缓存（可选）
- 在上传界面点击“清理缓存”按钮，可一键清理所有临时文件和缩略图

---

## 项目结构

```
pdf_color_inverter/
├── app.py                 # Flask主程序
├── requirements.txt       # Python依赖包
├── README.md             # 项目说明
├── static/               # 静态文件
│   ├── css/
│   │   └── style.css     # 样式文件
│   ├── js/
│   │   └── main.js       # JavaScript文件
│   └── thumbnails/       # 缩略图存储目录
├── templates/            # HTML模板
│   └── index.html        # 主页面
├── uploads/              # 上传文件存储目录
├── outputs/              # 处理后文件存储目录
├── package/              # 打包生成的exe和相关文件
└── logo.ico              # 程序图标
```

---

## API接口

### POST /upload
上传PDF文件并生成缩略图

**请求**：
- Content-Type: multipart/form-data
- 参数：pdf (文件)

**响应**：
```json
{
    "success": true,
    "file_id": "uuid",
    "thumbnails": ["/static/thumbnails/xxx.png"],
    "totalPages": 10,
    "original_name": "document.pdf"
}
```

### POST /process
处理选中的页面

**请求**：
```json
{
    "selectedPages": [0, 2, 5]
}
```

**响应**：
```json
{
    "success": true,
    "downloadUrl": "/download/filename.pdf",
    "message": "成功处理 3 页"
}
```

### GET /download/<filename>
下载处理后的PDF文件

---

## 配置说明

在 `app.py` 中可以修改以下配置：

- `MAX_CONTENT_LENGTH`：最大文件上传大小（默认50MB）
- `UPLOAD_FOLDER`：上传文件存储目录
- `THUMBNAIL_FOLDER`：缩略图存储目录
- `OUTPUT_FOLDER`：处理后文件存储目录

---

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

---

## 注意事项

1. 确保有足够的磁盘空间存储上传的文件和生成的缩略图
2. 大文件处理可能需要较长时间，请耐心等待
3. 建议定期清理 `uploads` 和 `outputs` 目录中的临时文件

---


## 其它说明

- **作者**：tinsy
- **项目主页**：[https://github.com/tinsyding/pdf_color_inverter](https://github.com/tinsyding/pdf_color_inverter)
- **安装包下载**：请前往 Releases 页面下载最新版安装包
- **反馈与建议**：欢迎提 Issue 或 Pull Request

---

## 许可证

MIT License