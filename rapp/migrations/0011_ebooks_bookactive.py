# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-13 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0010_ebooks_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebooks',
            name='bookActive',
            field=models.CharField(choices=[('bookActive', 'bookActive'), ('bookInactive', 'bookInactive')], default='bookActive', max_length=20),
        ),
    ]
