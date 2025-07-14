#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 页面反色工具 - 启动脚本
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

# 新增：保证工作目录为exe所在目录
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = ['flask', 'fitz', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'fitz':
                import fitz
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包：")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖：")
        print("pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """创建必要的目录"""
    directories = ['uploads', 'outputs', 'static/thumbnails']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录已创建: {directory}")

def main():
    """主函数"""
    print("🚀 PDF 页面反色工具 - Web版")
    print("=" * 50)
    
    # 检查依赖
    print("📦 检查依赖包...")
    if not check_dependencies():
        input("\n按回车键退出...")
        sys.exit(1)
    print("✅ 依赖包检查完成")
    
    # 创建目录
    print("\n📁 创建必要目录...")
    create_directories()
    
    # 启动应用
    print("\n🌐 启动Web服务器...")
    print("   服务器地址: http://localhost:4999")
    print("   按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 延迟打开浏览器
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:4999')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 导入并运行Flask应用
        from app import app
        app.run(debug=False, host='0.0.0.0', port=4999)
        
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        input("\n按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main() 