# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-02 12:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0015_auto_20181102_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='musicgenre',
            name='image',
            field=models.ImageField(null=True, upload_to='musicgenre/'),
        ),
    ]
