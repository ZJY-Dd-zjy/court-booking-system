#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成软著"程序鉴别材料"PDF
用法: python generate_source_pdf.py
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==================== 配置区 ====================
SOFTWARE_NAME = "智能体育场馆预约与分配系统 V1.0"
LINES_PER_PAGE = 50        # 每页行数（软著要求不少于50行）
FONT_SIZE = 10             # 字号
LEFT_MARGIN = 72           # 左边距
TOP_MARGIN = 72            # 上边距
LINE_HEIGHT = 14           # 行高

# 要包含的源代码文件（按顺序）
SOURCE_FILES = [
    'app.py',
    'sa_duiqi.py',
    'neural_fitness.py',
    'sa_demo.py',
    # 如需加入HTML文件，取消下面注释：
    # 'login.html',
    # 'my.html',
    # 'courts.html',
    # 'admin.html',
]

OUTPUT_DIR = '软著申请材料'
# =================================================

def register_font():
    """注册中文字体（Windows 宋体）"""
    font_paths = [
        'C:/Windows/Fonts/simsun.ttc',      # Windows 宋体
        'C:/Windows/Fonts/simhei.ttf',      # Windows 黑体
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', path))
                return 'ChineseFont'
            except Exception:
                continue
    # 如果没有中文字体，用内置Courier（纯英文代码也够）
    return 'Courier'

def read_source_files(files):
    """读取所有源代码文件"""
    all_lines = []
    for filename in files:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.exists(filepath):
            print(f"[警告] 文件不存在，跳过: {filepath}")
            continue
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        # 添加文件分隔标记
        all_lines.append(f"# {'='*60}\n")
        all_lines.append(f"# 文件: {filename}\n")
        all_lines.append(f"# {'='*60}\n")
        all_lines.extend(lines)
        if not lines[-1].endswith('\n'):
            all_lines.append('\n')
    return all_lines

def create_pdf(lines, output_path, start_page_num=1):
    """生成PDF，返回页数"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    font_name = register_font()
    
    page_num = start_page_num
    line_count = 0
    y = height - TOP_MARGIN
    
    for line in lines:
        # 新页面
        if line_count >= LINES_PER_PAGE:
            c.showPage()
            page_num += 1
            line_count = 0
            y = height - TOP_MARGIN
        
        # 第一行：画页眉
        if line_count == 0:
            c.setFont(font_name, 8)
            c.drawString(LEFT_MARGIN, height - 50, f"{SOFTWARE_NAME}    第 {page_num} 页")
            c.line(LEFT_MARGIN, height - 55, width - LEFT_MARGIN, height - 55)
        
        # 画代码行
        c.setFont(font_name, FONT_SIZE)
        text = line.rstrip('\n')
        # 如果一行太长，截断并加省略号
        max_chars = 90
        if len(text) > max_chars:
            text = text[:max_chars] + '...'
        c.drawString(LEFT_MARGIN, y, text)
        
        y -= LINE_HEIGHT
        line_count += 1
    
    c.save()
    return page_num - start_page_num + 1

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 50)
    print("软著程序鉴别材料生成工具")
    print("=" * 50)
    
    # 读取代码
    all_lines = read_source_files(SOURCE_FILES)
    total_lines = len(all_lines)
    total_pages = (total_lines + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    
    print(f"\n源代码文件数: {len(SOURCE_FILES)}")
    print(f"总行数: {total_lines}")
    print(f"预计页数（每页{LINES_PER_PAGE}行）: {total_pages}")
    
    if total_lines == 0:
        print("[错误] 没有读取到任何代码，请检查文件路径！")
        sys.exit(1)
    
    # 判断提交策略
    if total_lines > 3000:
        print(f"\n总行数 > 3000，按规则提交: 前30页 + 后30页")
        
        front_lines = all_lines[:30 * LINES_PER_PAGE]
        back_lines = all_lines[-30 * LINES_PER_PAGE:]
        
        front_path = os.path.join(OUTPUT_DIR, '程序鉴别材料_前30页.pdf')
        back_path = os.path.join(OUTPUT_DIR, '程序鉴别材料_后30页.pdf')
        
        pages1 = create_pdf(front_lines, front_path, start_page_num=1)
        pages2 = create_pdf(back_lines, back_path, start_page_num=31)
        
        print(f"\n[完成] 前30页已生成: {front_path} ({pages1}页)")
        print(f"[完成] 后30页已生成: {back_path} ({pages2}页)")
        print(f"\n请分别上传这两个PDF到软著申请系统！")
        
    else:
        print(f"\n总行数 <= 3000，按规则: 全部提交")
        
        output_path = os.path.join(OUTPUT_DIR, '程序鉴别材料_全部.pdf')
        pages = create_pdf(all_lines, output_path, start_page_num=1)
        
        print(f"\n[完成] 全部代码已生成: {output_path} ({pages}页)")
        print(f"\n请将此PDF上传到软著申请系统！")
    
    print(f"\n输出目录: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == '__main__':
    # 检查 reportlab
    try:
        import reportlab
    except ImportError:
        print("[错误] 缺少 reportlab 库，请先安装:")
        print("  pip install reportlab")
        sys.exit(1)
    
    main()
