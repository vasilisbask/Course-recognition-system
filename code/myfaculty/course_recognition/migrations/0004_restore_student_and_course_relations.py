# Generated manually to align course recognition with the approved class diagram.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_recognition", "0003_remove_courserecognitionrequest_student_and_more"),
        ("curricula", "0002_initial"),
        ("myprofile", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="courserecognitionrequest",
            name="student",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="course_recognition_requests",
                to="myprofile.student",
                verbose_name="Φοιτητής",
            ),
        ),
        migrations.AlterField(
            model_name="courserecognitionrequest",
            name="course",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="recognition_requests",
                to="curricula.course",
                verbose_name="Μάθημα προς αναγνώριση",
            ),
        ),
        migrations.AlterField(
            model_name="courserecognitionrequest",
            name="full_name",
            field=models.CharField(blank=True, max_length=255, verbose_name="Ονοματεπώνυμο"),
        ),
        migrations.AlterField(
            model_name="courserecognitionrequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("SUBMITTED", "Υποβλήθηκε"),
                    ("UNDER_REVIEW", "Υπό εξέταση"),
                    ("APPROVED", "Εγκρίθηκε"),
                    ("REJECTED", "Απορρίφθηκε"),
                    ("WITHDRAWN", "Αποσύρθηκε / Μη ενεργή"),
                ],
                default="UNDER_REVIEW",
                max_length=20,
                verbose_name="Κατάσταση",
            ),
        ),
        migrations.AlterField(
            model_name="courserecognitionrecommendation",
            name="professor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="course_recognition_recommendations",
                to="myprofile.staffmember",
                verbose_name="Καθηγητής",
            ),
        ),
    ]
