from django.db import migrations


def backfill_secretariat_submitters(apps, schema_editor):
    Recommendation = apps.get_model("course_recognition", "CourseRecognitionRecommendation")
    Secretariat = apps.get_model("scopes", "Secretariat")

    recommendations = Recommendation.objects.filter(
        submitted_by_secretariat=True,
        submitted_by_user__isnull=True,
    ).select_related("request__course")

    for recommendation in recommendations:
        course = getattr(recommendation.request, "course", None)
        if not course or not course.program_id:
            continue

        secretariat = (
            Secretariat.objects
            .filter(programs=course.program_id, user__isnull=False)
            .order_by("id")
            .first()
        )
        if secretariat:
            recommendation.submitted_by_user_id = secretariat.user_id
            recommendation.save(update_fields=["submitted_by_user"])


class Migration(migrations.Migration):

    dependencies = [
        ("course_recognition", "0008_recommendation_submitted_by_user"),
        ("scopes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(backfill_secretariat_submitters, migrations.RunPython.noop),
    ]
