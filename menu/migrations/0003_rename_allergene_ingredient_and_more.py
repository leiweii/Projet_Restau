# Generated by Django 5.1.7 on 2025-03-26 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_allergene_plat_allergenes'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Allergene',
            new_name='Ingredient',
        ),
        migrations.RenameField(
            model_name='plat',
            old_name='allergenes',
            new_name='ingredients',
        ),
    ]
