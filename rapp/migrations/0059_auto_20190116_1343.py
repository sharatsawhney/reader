# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-16 13:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0058_facebookid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboard',
            name='itime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]