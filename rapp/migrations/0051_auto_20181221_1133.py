# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-21 11:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0050_publisherpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploaded',
            name='file',
            field=models.CharField(max_length=255),
        ),
    ]