"""
生成符合中国版权保护中心要求的软著申请材料
- 源代码文档：每页50行，页眉含软件名称+版本号
- 软件说明书文档：A4格式
"""
import sys
from pathlib import Path

# 添加 python-docx 路径（如需要）
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn

PROJECT_DIR = Path("C:/Users/five_/PycharmProjects/FlaskProject")
OUTPUT_DIR = Path("C:/Users/five_/PycharmProjects/FlaskProject/软著申请材料")
OUTPUT_DIR.mkdir(exist_ok=True)

SOFTWARE_NAME = "基于模拟退火算法的高校体育场馆智能预约系统"
VERSION = "V1.0"
LINES_PER_PAGE = 50

# ============ 1. 生成源代码文档 ============

def generate_source_code_doc():
    doc = Document()
    
    # 设置页面：A4，窄边距
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)
    
    # 设置页眉
    header = section.header
    header_para = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    header_para.text = f"{SOFTWARE_NAME} {VERSION}"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in header_para.runs:
        run.font.size = Pt(10)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    # 设置页脚（页码）
    footer = section.footer
    footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 代码文件顺序
    code_files = [
        ("app.py", "Flask后端主程序"),
        ("sa_duiqi.py", "模拟退火算法模块"),
        ("login.html", "登录页面"),
        ("courts.html", "场地看板页面"),
        ("my.html", "我的预约页面"),
        ("admin.html", "管理员页面"),
    ]
    
    all_lines = []
    for filename, desc in code_files:
        filepath = PROJECT_DIR / filename
        if not filepath.exists():
            continue
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        all_lines.append((filename, desc, lines))
    
    # 添加标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"{SOFTWARE_NAME}\n源代码")
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.name = '黑体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    doc.add_paragraph()  # 空行
    
    line_count = 0
    for filename, desc, lines in all_lines:
        # 文件分隔标题
        sep = doc.add_paragraph()
        sep_run = sep.add_run(f"# ===== {filename} ({desc}) =====")
        sep_run.font.size = Pt(10)
        sep_run.font.name = 'Courier New'
        sep_run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Courier New')
        line_count += 1
        
        for line in lines:
            # 去除尾部换行，但保留内容
            content = line.rstrip('\n').rstrip('\r')
            if not content:
                content = " "  # 空行保留一个空格
            
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = Pt(14)
            run = p.add_run(content)
            run.font.size = Pt(9)
            run.font.name = 'Courier New'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Courier New')
            line_count += 1
            
            # 每50行插入分页符（页眉/页脚会自动延续）
            if line_count % LINES_PER_PAGE == 0:
                doc.add_page_break()
    
    output_path = OUTPUT_DIR / "软著-源代码.docx"
    doc.save(output_path)
    print(f"源代码文档已生成：{output_path}（共约{line_count}行）")
    return output_path

# ============ 2. 生成软件说明书文档 ============

def generate_manual_doc():
    doc = Document()
    
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)
    
    # 页眉
    header = section.header
    header_para = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    header_para.text = f"{SOFTWARE_NAME} {VERSION}"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in header_para.runs:
        run.font.size = Pt(10)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    # 标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f"{SOFTWARE_NAME}\n软件说明书")
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.name = '黑体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    doc.add_paragraph()
    
    # 内容
    content = [
        ("一、软件概述", [
            f"软件全称：{SOFTWARE_NAME}",
            f"软件简称：场馆预约系统",
            f"版本号：{VERSION}",
            f"开发完成日期：2026年8月",
            "",
            "本软件是一款面向高校体育场馆的智能化预约管理平台，通过模拟退火算法实现场地资源的全局最优分配，解决传统预约系统中存在的场地冲突、分配不均、用户偏好匹配度低等问题。",
        ]),
        ("二、开发环境", [
            "操作系统：Windows 10/11",
            "开发语言：Python 3.10",
            "Web框架：Flask 2.3",
            "数据库：SQLite 3",
            "前端技术：HTML5 + CSS3 + JavaScript + Bootstrap",
            "算法库：NumPy",
        ]),
        ("三、软件功能模块", [
            "本系统由三大核心模块组成：用户端、管理端、算法引擎。",
            "",
            "3.1 用户端功能",
            "（1）用户管理：支持用户注册、登录，普通用户与管理员角色区分；",
            "（2）场地浏览：查看场地列表、类型、位置、实时状态（空闲/预约中/已使用）；",
            "（3）智能推荐：基于历史预约记录，综合类型匹配（50%）、楼层匹配（30%）、时段匹配（20%）权重推荐偏好场地；",
            "（4）在线预约：选择场地、日期、时段，提交预约；",
            "（5）我的预约：查看预约记录、签到、取消预约。",
            "",
            "3.2 管理端功能",
            "（1）全局优化：执行模拟退火算法，计算最优场地分配方案；",
            "（2）匹配率统计：查看理论匹配率与实际匹配率对比；",
            "（3）用户管理：查看普通用户列表及偏好分析；",
            "（4）超时释放：自动释放15分钟未签到的预约。",
            "",
            "3.3 算法引擎功能",
            "（1）模拟退火优化：带时间维度和场地唯一性约束的全局优化；",
            "（2）适应度计算：综合类型匹配、时段匹配、楼层匹配的评分；",
            "（3）约束检查：确保同一时段同一场地只分配给一个用户；",
            "（4）多参数调优：支持温度、迭代次数、冷却系数等参数调整。",
        ]),
        ("四、软件使用说明", [
            "4.1 用户注册与登录",
            "打开系统首页，新用户点击\"注册\"按钮，填写用户名、密码。输入邀请码\"ADMIN2024\"可注册为管理员。注册成功后使用用户名和密码登录。",
            "",
            "4.2 场地预约",
            "登录后进入\"场地看板\"页面，系统会根据用户历史预约记录自动推荐场地。点击空闲场地，弹出预约窗口，选择日期和时间段，确认后完成预约。",
            "",
            "4.3 签到与取消",
            "在\"我的预约\"页面，可对\"预约中\"的订单进行签到或取消。系统会在预约后15分钟自动检查，未签到则自动释放场地。",
            "",
            "4.4 全局优化（管理员）",
            "管理员登录后进入\"全局优化\"页面，点击\"执行全局优化\"按钮，系统调用模拟退火算法，综合考虑所有用户的场地偏好、时段偏好，计算最优分配方案。",
        ]),
        ("五、软件技术特点", [
            "1. 智能推荐算法：基于用户历史预约数据，采用加权评分机制精准推荐偏好场地。",
            "2. 模拟退火全局优化：引入模拟退火算法解决场地分配问题，在合理时间内收敛到最优解。",
            "3. 并发安全控制：采用数据库事务锁机制，确保高并发场景下场地预约的一致性。",
            "4. 超时自动释放：设置15分钟签到超时机制，未按时签到的预约自动取消并释放场地资源。",
            "5. 响应式布局：采用Bootstrap栅格系统，适配PC端和移动端浏览器。",
        ]),
        ("六、软件界面说明", [
            "本软件主要包含以下界面：",
            "（1）登录/注册页面：用户入口，支持普通用户和管理员两种角色；",
            "（2）场地看板页面：展示所有场地状态，支持智能推荐和在线预约；",
            "（3）我的预约页面：展示个人预约记录，支持签到和取消；",
            "（4）全局优化页面（管理员）：展示优化结果和匹配率统计。",
            "（界面截图见附件）",
        ]),
    ]
    
    for heading, paras in content:
        # 一级标题
        h = doc.add_paragraph()
        run = h.add_run(heading)
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.name = '黑体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        h.paragraph_format.space_after = Pt(6)
        
        # 正文
        for para in paras:
            p = doc.add_paragraph()
            run = p.add_run(para)
            run.font.size = Pt(12)
            run.font.name = '宋体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            p.paragraph_format.first_line_indent = Cm(0.74) if para and not para.startswith("（") else Cm(0)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(3)
    
    output_path = OUTPUT_DIR / "软著-软件说明书.docx"
    doc.save(output_path)
    print(f"软件说明书已生成：{output_path}")
    return output_path

if __name__ == "__main__":
    generate_source_code_doc()
    generate_manual_doc()
    print("\n全部完成！请检查软著申请材料文件夹。")
