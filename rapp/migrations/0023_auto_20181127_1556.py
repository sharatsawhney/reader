# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-27 15:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0022_auto_20181127_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='highlight',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]