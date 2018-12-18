# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-04 05:49
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0033_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='percentval',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='offer',
            name='trueoffer',
            field=models.BooleanField(default=False),
        ),
    ]
