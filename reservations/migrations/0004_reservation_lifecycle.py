import uuid

from django.db import migrations, models


def assign_unique_tokens(apps, schema_editor):
    Reservation = apps.get_model("reservations", "Reservation")
    for reservation in Reservation.objects.all().iterator():
        reservation.management_token = uuid.uuid4()
        reservation.save(update_fields=["management_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("reservations", "0003_reservationdaylock"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="status",
            field=models.CharField(
                choices=[
                    ("confirmed", "Confirmée"),
                    ("cancelled", "Annulée"),
                    ("seated", "Installée"),
                    ("completed", "Terminée"),
                    ("no_show", "Non présentée"),
                ],
                default="confirmed",
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name="reservation",
            name="management_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.RunPython(assign_unique_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="reservation",
            name="management_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="reservation",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
