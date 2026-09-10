from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("course_recognition", "0005_limit_request_uploads_to_pdf"),
    ]

    operations = [
        migrations.AddField(
            model_name="courserecognitionrequest",
            name="withdrawal_reason",
            field=models.TextField(blank=True, verbose_name="Αιτιολόγηση διαγραφής"),
        ),
        migrations.AddField(
            model_name="courserecognitionrequest",
            name="withdrawn_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Ημερομηνία διαγραφής"),
        ),
        migrations.AddField(
            model_name="courserecognitionrequest",
            name="withdrawn_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="withdrawn_course_recognition_requests",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Διαγραφή από",
            ),
        ),
    ]
