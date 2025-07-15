from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import fitz  # PyMuPDF
from PIL import Image
import io
import datetime
import uuid
import platform
import signal
import shutil
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'static'),
    template_folder=os.path.join(BASE_DIR, 'templates')
)

app.secret_key = 'tinsy_key_level_1'

# 配置
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 最大文件大小
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['THUMBNAIL_FOLDER'] = os.path.join(BASE_DIR, 'static', 'thumbnails')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, 'outputs')

# 确保目录存在
for folder in [app.config['UPLOAD_FOLDER'], app.config['THUMBNAIL_FOLDER'], app.config['OUTPUT_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# 存储当前会话的文件信息
session_files = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        # 自动清理旧文件
        for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['THUMBNAIL_FOLDER']]:
            clear_old_files(folder)
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        file = request.files['pdf']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': '请选择PDF文件'})
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 确保uploads目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # 保存文件
        file.save(filepath)
        
        # 生成缩略图
        thumbnails = generate_thumbnails(filepath, file_id)
        
        # 获取PDF页数
        pdf = fitz.open(filepath)
        total_pages = len(pdf)
        pdf.close()
        
        # 存储文件信息
        session_files[file_id] = {
            'filepath': filepath,
            'original_name': file.filename,
            'upload_time': datetime.datetime.now()
        }
        session['file_id'] = file_id  # 存入session
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'thumbnails': thumbnails,
            'totalPages': total_pages,
            'original_name': file.filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process', methods=['POST'])
def process_pdf():
    try:
        # 自动清理旧文件
        for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['THUMBNAIL_FOLDER']]:
            clear_old_files(folder)
        data = request.get_json()
        selected_pages = data.get('selectedPages', [])
        file_id = data.get('file_id') or session.get('file_id')
        if not selected_pages:
            return jsonify({'success': False, 'error': '请选择要处理的页面'})
        if not file_id or file_id not in session_files:
            return jsonify({'success': False, 'error': '未找到上传的文件'})
        file_info = session_files[file_id]
        input_path = file_info['filepath']
        # 生成输出文件名
        base_name = os.path.splitext(file_info['original_name'])[0]
        output_filename = f"{base_name}_反色_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        # 处理PDF
        process_pdf_colors(input_path, output_path, selected_pages)
        # 返回下载链接
        download_url = f"/download/{output_filename}"
        return jsonify({
            'success': True,
            'downloadUrl': download_url,
            'message': f'成功处理 {len(selected_pages)} 页，文件已保存为 {output_filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        # 优先用 session 里的 file_id 检查权限（可选，简单实现）
        # file_id = session.get('file_id')
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    try:
        cleared = []
        for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['THUMBNAIL_FOLDER']]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        cleared.append(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        cleared.append(file_path)
                except Exception as e:
                    print(f'无法删除 {file_path}: {e}')
        return jsonify({'success': True, 'message': f'已清理 {len(cleared)} 个缓存文件'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return '服务器正在关闭...'

def generate_thumbnails(pdf_path, file_id):
    """生成PDF页面缩略图"""
    thumbnails = []
    
    try:
        pdf = fitz.open(pdf_path)
        
        for page_num in range(len(pdf)):
            # 获取页面图像
            page = pdf.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # 缩放50%
            
            # 转换为PIL图像
            img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # 调整大小
            img_data.thumbnail((200, 280), Image.Resampling.LANCZOS)
            
            # 保存缩略图
            thumbnail_filename = f"{file_id}_page_{page_num}.png"
            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
            img_data.save(thumbnail_path, "PNG")
            
            # 返回URL
            thumbnail_url = f"/static/thumbnails/{thumbnail_filename}"
            thumbnails.append(thumbnail_url)
        
        pdf.close()
        
    except Exception as e:
        print(f"生成缩略图失败: {e}")
    
    return thumbnails

def process_pdf_colors(input_path, output_path, selected_pages, dpi=300):
    """处理PDF颜色反转"""
    try:
        input_pdf = fitz.open(input_path)
        output_pdf = fitz.open()
        
        total_pages = len(input_pdf)
        
        for page_num in range(total_pages):
            page = input_pdf[page_num]
            
            if page_num in selected_pages:
                # 反转颜色
                pix = page.get_pixmap(dpi=dpi)
                pix.invert_irect()
                img_bytes = pix.tobytes("png")
                new_page = output_pdf.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_image(new_page.rect, stream=io.BytesIO(img_bytes))
            else:
                # 保持原样
                output_pdf.insert_pdf(input_pdf, from_page=page_num, to_page=page_num)
        
        # 保存文件
        output_pdf.save(output_path, garbage=4, deflate=True, clean=True)
        
        input_pdf.close()
        output_pdf.close()
        
    except Exception as e:
        raise Exception(f"处理PDF时发生错误: {e}")

def clear_old_files(folder, expire_seconds=3600):
    now = time.time()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > expire_seconds:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f'无法删除 {file_path}: {e}')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=4999) 