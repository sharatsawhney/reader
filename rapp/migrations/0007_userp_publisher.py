# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-11 14:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0006_auto_20180511_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='userp',
            name='publisher',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='rapp.Publishers'),
        ),
    ]
