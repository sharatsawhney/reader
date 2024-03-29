# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-01 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authors',
            name='publisher_name',
        ),
        migrations.RemoveField(
            model_name='ebooks',
            name='link',
        ),
        migrations.AddField(
            model_name='ebooks',
            name='ratedusers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ebooks',
            name='rating',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='ebooks',
            name='content',
            field=models.FileField(blank=True, default='', upload_to='epub/'),
        ),
    ]
