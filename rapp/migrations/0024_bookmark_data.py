# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-29 12:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0023_auto_20181127_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookmark',
            name='data',
            field=models.TextField(default=''),
        ),
    ]