# Generated by Django 5.0 on 2024-02-02 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0003_alter_account_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='code',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]