# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-01 10:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0008_remove_ebooks_publishdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebooks',
            name='tags',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
