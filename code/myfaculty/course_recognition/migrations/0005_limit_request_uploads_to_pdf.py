from django.core.validators import FileExtensionValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_recognition", "0004_restore_student_and_course_relations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="courserecognitionrequest",
            name="course_description_file",
            field=models.FileField(
                upload_to="course_recognition/course_descriptions/",
                validators=[FileExtensionValidator(allowed_extensions=("pdf",))],
                verbose_name="Περιγραφή μαθήματος",
            ),
        ),
        migrations.AlterField(
            model_name="courserecognitionrequest",
            name="transcript_file",
            field=models.FileField(
                upload_to="course_recognition/transcripts/",
                validators=[FileExtensionValidator(allowed_extensions=("pdf",))],
                verbose_name="Αναλυτική βαθμολογία",
            ),
        ),
        migrations.AlterField(
            model_name="courserecognitionrequest",
            name="degree_file",
            field=models.FileField(
                upload_to="course_recognition/degrees/",
                validators=[FileExtensionValidator(allowed_extensions=("pdf",))],
                verbose_name="Πτυχίο",
            ),
        ),
    ]
