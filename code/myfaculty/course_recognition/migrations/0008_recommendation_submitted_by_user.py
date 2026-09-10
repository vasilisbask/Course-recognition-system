from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("course_recognition", "0007_remove_submitted_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="courserecognitionrecommendation",
            name="submitted_by_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="course_recognition_submitted_recommendations",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Συμπληρώθηκε από χρήστη",
            ),
        ),
    ]
