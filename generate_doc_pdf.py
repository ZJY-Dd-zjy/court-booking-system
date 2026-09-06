#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成软著"文档鉴别材料"PDF
用法: python generate_doc_pdf.py
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==================== 配置区 ====================
SOFTWARE_NAME = "智能体育场馆预约与分配系统 V1.0"
LINES_PER_PAGE = 30        # 文档每页行数（软著要求不少于30行）
FONT_SIZE = 12             # 字号（比代码大一点）
LEFT_MARGIN = 72           # 左边距
TOP_MARGIN = 72            # 上边距
LINE_HEIGHT = 20           # 行高

# 要包含的文档文件（Markdown）
DOC_FILE = '软著申请材料/用户使用手册.md'
OUTPUT_DIR = '软著申请材料'
# =================================================

def register_font():
    """注册中文字体（Windows 宋体）"""
    font_paths = [
        'C:/Windows/Fonts/simsun.ttc',
        'C:/Windows/Fonts/simhei.ttf',
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', path))
                return 'ChineseFont'
            except Exception:
                continue
    return 'Courier'

def read_doc(filepath):
    """读取文档文件"""
    if not os.path.exists(filepath):
        print(f"[错误] 文件不存在: {filepath}")
        sys.exit(1)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.readlines()

def create_pdf(lines, output_path, start_page_num=1):
    """生成PDF，返回页数"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    font_name = register_font()
    
    page_num = start_page_num
    line_count = 0
    y = height - TOP_MARGIN
    
    for line in lines:
        if line_count >= LINES_PER_PAGE:
            c.showPage()
            page_num += 1
            line_count = 0
            y = height - TOP_MARGIN
        
        if line_count == 0:
            c.setFont(font_name, 9)
            c.drawString(LEFT_MARGIN, height - 50, f"{SOFTWARE_NAME}    第 {page_num} 页")
            c.line(LEFT_MARGIN, height - 55, width - LEFT_MARGIN, height - 55)
        
        c.setFont(font_name, FONT_SIZE)
        text = line.rstrip('\n')
        # 文档可以更长一些，每行100字符
        max_chars = 100
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
    print("软著文档鉴别材料生成工具")
    print("=" * 50)
    
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), DOC_FILE)
    all_lines = read_doc(filepath)
    total_lines = len(all_lines)
    total_pages = (total_lines + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    
    print(f"\n文档文件: {DOC_FILE}")
    print(f"总行数: {total_lines}")
    print(f"预计页数（每页{LINES_PER_PAGE}行）: {total_pages}")
    
    if total_lines == 0:
        print("[错误] 文档为空！")
        sys.exit(1)
    
    if total_pages < 15:
        print(f"\n[警告] 文档仅{total_pages}页，建议补充到15页以上再提交！")
        print("可继续生成，但审查可能不通过。")
    
    # 文档材料：前30页 + 后30页（如果超过60页）
    if total_lines > 60 * LINES_PER_PAGE:
        print(f"\n总行数 > {60 * LINES_PER_PAGE}，按规则提交: 前30页 + 后30页")
        
        front_lines = all_lines[:30 * LINES_PER_PAGE]
        back_lines = all_lines[-30 * LINES_PER_PAGE:]
        
        front_path = os.path.join(OUTPUT_DIR, '文档鉴别材料_前30页.pdf')
        back_path = os.path.join(OUTPUT_DIR, '文档鉴别材料_后30页.pdf')
        
        pages1 = create_pdf(front_lines, front_path, start_page_num=1)
        pages2 = create_pdf(back_lines, back_path, start_page_num=31)
        
        print(f"\n[完成] 前30页已生成: {front_path} ({pages1}页)")
        print(f"[完成] 后30页已生成: {back_path} ({pages2}页)")
        print(f"\n请分别上传这两个PDF到软著申请系统！")
        
    else:
        print(f"\n总行数 <= {60 * LINES_PER_PAGE}，按规则: 全部提交")
        
        output_path = os.path.join(OUTPUT_DIR, '文档鉴别材料_全部.pdf')
        pages = create_pdf(all_lines, output_path, start_page_num=1)
        
        print(f"\n[完成] 全部文档已生成: {output_path} ({pages}页)")
        print(f"\n请将此PDF上传到软著申请系统！")
    
    print(f"\n输出目录: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == '__main__':
    try:
        import reportlab
    except ImportError:
        print("[错误] 缺少 reportlab 库，请先安装:")
        print("  pip install reportlab")
        sys.exit(1)
    
    main()
