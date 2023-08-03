# Generated by Django 4.1.2 on 2023-08-03 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='rated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='link',
            name='total_ratings',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='link',
            name='total_score',
            field=models.IntegerField(default=0),
        ),
    ]