# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-18 11:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0013_auto_20180531_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebooks',
            name='isbn',
            field=models.CharField(default='', max_length=14, unique=True),
        ),
    ]
