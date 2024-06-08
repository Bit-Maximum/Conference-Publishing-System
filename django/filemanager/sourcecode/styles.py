from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_COLOR_INDEX
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.dml import MSO_THEME_COLOR_INDEX


def reset_paragraph_style(paragraph):
    paragraph.paragraph_format.left_indent = Cm(0)
    paragraph.paragraph_format.right_indent = Cm(0)
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.paragraph_format.widow_control = True
    paragraph.paragraph_format.space_after = Cm(0)


def reset_run_style(run):
    run.font.bold = False
    run.font.color.rgb = None
    run.font.size = Pt(12)
    run.font.name = "Times New Roman"
    run.font.all_caps = False


def paragraph_default_style(p_out, p_in=None):
    p_out.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    p_out.paragraph_format.line_spacing = 1.15
    p_out.paragraph_format.widow_control = True
    p_out.paragraph_format.space_after = Cm(0)

    p_out.paragraph_format.first_line_indent = Cm(1.25)
    p_out.paragraph_format.left_indent = Cm(0)
    p_out.paragraph_format.right_indent = Cm(0)


def run_default_style(run_out, run_in=None):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = run_in.font.bold if run_in else None
    run_out.italic = run_in.italic if run_in else None


def style_authors_names(run):
    reset_run_style(run)
    run.font.bold = True


def style_collection_authors_names(run):
    reset_run_style(run)
    run.font.size = Pt(14)
    run.italic = True


def style_heading_text(run):
    reset_run_style(run)


def style_title(run, font_size=12):
    reset_run_style(run)
    run.font.bold = True
    run.font.size = Pt(font_size)
    run.font.all_caps = True


def style_abstract_or_keywords(run):
    reset_run_style(run)
    run.font.bold = False
    run.italic = True


def subtext_picture_style(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = None
    run_out.italic = None


def prefix_picture_style(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = None
    run_out.italic = True


def set_style_table_prefix(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = None
    run_out.italic = True


def set_style_table_name(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = False
    run_out.italic = None


def set_style_default_table(table, font_size=10):
    table.style = 'Table Grid'
    table.autofit = True
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.line_spacing = 1.15
                for run in paragraph.runs:
                    run.font.size = Pt(font_size)
                    run.font.name = 'Times New Roman'

    for cell in table.rows[0].cells:
        for paragraph in cell.paragraphs:
            paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


def set_default_style(document, output_path):
    custom_style = document.styles["Normal"]
    custom_style.font.name = 'Times New Roman'
    custom_style.font.size = Pt(10)
    custom_style.font.bold = False
    custom_style.paragraph_format.left_indent = Pt(0)
    custom_style.paragraph_format.first_line_indent = Pt(0)
    custom_style.paragraph_format.widow_control = True
    custom_style.paragraph_format.line_spacing = 1.15

    custom_style = document.styles["List Number"]
    custom_style.font.size = Pt(12)
    document.save(output_path)


def set_styles(document, output_path):
    custom_style = document.styles["Normal"]
    custom_style.font.name = 'Times New Roman'
    custom_style.font.size = Pt(10)
    custom_style.font.bold = False
    custom_style.paragraph_format.left_indent = Pt(0)
    custom_style.paragraph_format.first_line_indent = Pt(0)
    custom_style.paragraph_format.widow_control = True
    custom_style.paragraph_format.line_spacing = 1.15

    custom_style = document.styles["List Number"]
    custom_style.font.size = Pt(14)

    custom_style = document.styles["Heading 1"]
    custom_style.font.name = 'Times New Roman'
    custom_style.font.size = Pt(16)
    custom_style.font.bold = True
    custom_style.font.color.rgb = None
    custom_style.paragraph_format.left_indent = Pt(0)
    custom_style.paragraph_format.first_line_indent = Pt(0)
    custom_style.paragraph_format.widow_control = True
    custom_style.paragraph_format.line_spacing = 1.30

    custom_style = document.styles["Heading 2"]
    custom_style.font.name = 'Times New Roman'
    custom_style.font.size = Pt(15)
    custom_style.font.bold = True
    custom_style.font.color.rgb = None
    custom_style.paragraph_format.left_indent = Pt(0)
    custom_style.paragraph_format.first_line_indent = Pt(0)
    custom_style.paragraph_format.widow_control = True
    custom_style.paragraph_format.line_spacing = 1.15

    document.save(output_path)


def index_style(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = False
    run_out.italic = None


def default_italic_style(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = None
    run_out.italic = True


def collection_bold_style(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(12)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = True
    run_out.italic = None


def mark_style(run_out):
    index_style(run_out)
    run_out.font.highlight_color = WD_COLOR_INDEX.YELLOW


def collection_headings_style(run_out):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(16)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = True
    run_out.font.bold = True
    run_out.italic = None


def section_headings_style(run_out, font_size=16):
    run_out.font.color.rgb = None
    run_out.font.size = Pt(font_size)
    run_out.font.name = "Times New Roman"
    run_out.font.all_caps = False
    run_out.font.bold = True
    run_out.italic = None


def copy_paragraph_style(p_out, p_in):
    p_out.paragraph_format.alignment = p_in.paragraph_format.alignment
    p_out.paragraph_format.line_spacing = p_in.paragraph_format.line_spacing
    p_out.paragraph_format.widow_control = p_in.paragraph_format.widow_control
    p_out.paragraph_format.space_after = p_in.paragraph_format.space_after

    p_out.paragraph_format.first_line_indent = p_in.paragraph_format.first_line_indent
    p_out.paragraph_format.left_indent = p_in.paragraph_format.left_indent
    p_out.paragraph_format.right_indent = p_in.paragraph_format.right_indent


def copy_run_style(run_out, run_in):
    run_out.font.color.rgb = run_in.font.color.rgb
    run_out.font.size = run_in.font.size
    run_out.font.name = run_in.font.name
    run_out.font.all_caps = run_in.font.all_caps
    run_out.font.bold = run_in.font.bold
    run_out.italic = run_in.italic


def change_font_size(run_out, pt):
    run_out.font.size = Pt(pt)
