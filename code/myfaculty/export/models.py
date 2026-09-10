from django.db import models
from django.http import HttpResponse
from .utils import convert_to_docx , abs_tmp_filename, convert_multiple_to_docx

# Create your models here.


class DocumentTemplate(models.Model):
    name = models.CharField(max_length = 100)
    docx = models.FileField(upload_to='templates/')

    def __str__(self):
        return self.name + ' (' + self.docx.path + ')'
    
    def build_docx(self, d, target_filename):
        self.tmp_filename = abs_tmp_filename(target_filename)        
        convert_to_docx(self.docx.path, self.tmp_filename, d)

    def build_from_multiple_docx(self, dd, target_filename):
        self.tmp_filename = abs_tmp_filename(target_filename)        
        convert_multiple_to_docx(self.docx.path, self.tmp_filename, dd)
    
    def export_file_response(self, d):

        if isinstance(d, dict):
            self.build_docx(d, 'export.docx')
        elif isinstance(d, list):
            self.build_from_multiple_docx(d, 'export.docx')
        
        with open(self.tmp_filename, 'rb') as f:
           data = f.read()

        response = HttpResponse(
            data,
            content_type="text/docx",
            headers={"Content-Disposition": 'attachment; filename="export.docx" '},
        )

        return response