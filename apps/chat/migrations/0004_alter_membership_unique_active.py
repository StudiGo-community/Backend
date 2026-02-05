from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0003_remove_room_chat_room_updated_5097bc_idx_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="membership",
            name="unique_membership",
        ),
        migrations.AddConstraint(
            model_name="membership",
            constraint=models.UniqueConstraint(
                fields=("room", "user"),
                condition=models.Q(left_at__isnull=True),
                name="unique_active_membership",
            ),
        ),
    ]
