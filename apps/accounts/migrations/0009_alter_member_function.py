# Generated by Django 4.2 on 2025-05-04 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_memberfunctions_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="function",
            field=models.ManyToManyField(blank=True, to="accounts.memberfunctions"),
        ),
    ]
