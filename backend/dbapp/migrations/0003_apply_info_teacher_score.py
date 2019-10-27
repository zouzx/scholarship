# Generated by Django 2.1.4 on 2019-10-27 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbapp', '0002_applyinfo_extra_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='applyinfo',
            name='is_teacher_score_updated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='applyinfo',
            name='teacher_score',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='applyinfo',
            name='teacher_score_avg',
            field=models.FloatField(default=0),
        ),
    ]