# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-24 08:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scratch_api', '0005_auto_20170724_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='teacher',
            field=models.ManyToManyField(blank=True, null=True, to='scratch_api.Teacher'),
        ),
    ]
