# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-18 13:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0045_connectionhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectionhistory',
            name='echo',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
