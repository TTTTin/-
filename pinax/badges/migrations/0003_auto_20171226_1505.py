# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-26 07:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinax_badges', '0002_badgeaward_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgeaward',
            name='image',
            field=models.ImageField(default='./badegs1.png', upload_to='./'),
        ),
    ]
