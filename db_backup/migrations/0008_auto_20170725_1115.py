# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-25 03:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scratch_api', '0007_auto_20170725_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherscore',
            name='comment',
            field=models.TextField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.ForeignKey(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.CASCADE, to='scratch_api.School'),
        ),
        migrations.AlterField(
            model_name='user',
            name='student_class',
            field=models.ForeignKey(blank=True, max_length=30, null=True, on_delete=django.db.models.deletion.CASCADE, to='scratch_api.Class'),
        ),
    ]