from django.db import migrations, models


def submitted_to_under_review(apps, schema_editor):
    CourseRecognitionRequest = apps.get_model("course_recognition", "CourseRecognitionRequest")
    CourseRecognitionRequest.objects.filter(status="SUBMITTED").update(status="UNDER_REVIEW")


class Migration(migrations.Migration):

    dependencies = [
        ("course_recognition", "0006_withdrawal_metadata"),
    ]

    operations = [
        migrations.RunPython(submitted_to_under_review, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="courserecognitionrequest",
            name="status",
            field=models.CharField(
                choices=[
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
    ]
