# Generated by Django 5.0 on 2024-01-31 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0015_productoffer_categoryoffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='referral',
            field=models.BooleanField(default=False),
        ),
    ]
