from docx import Document
from django.conf import settings
import os
from docxtpl import DocxTemplate
from docxcompose.composer import Composer
import io
from pathlib import Path
from django.template.loader import render_to_string
from weasyprint import HTML
from pypdf import PdfWriter, PdfReader


def convert_to_docx(template, output_file, d):
    doc = DocxTemplate(template)
    doc.render(d)
    doc.save(output_file)

def convert_multiple_to_docx(template, output_file, dd):
    for i, gc in enumerate(dd):
        doc = DocxTemplate( template )
        doc.render(gc)
        doc.save(output_file)

        if i==0:
            master = Document(output_file)
            composer = Composer(master)
        else:
            doc = Document(output_file)
            composer.append(doc)    
    composer.save(output_file)

def abs_tmp_filename(target_filename):
    tmp_media = settings.MEDIA_TMP_EXPORT  
    abs_filename = os.path.join(tmp_media, target_filename) 
    return abs_filename

def render_html_to_pdf(template_name, context):
    html_string = render_to_string(template_name, context)
    pdf_file = io.BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)
    return pdf_file

def append_pdf(writer, pdf_file):
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

def append_filefield(writer, filefield):
    if not filefield:
        return

    try:
        f=filefield.open("rb")
    except Exception:
        return
    
    reader = PdfReader(f)
    for page in reader.pages:
        writer.add_page(page)

    f.close()
