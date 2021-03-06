# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-01 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0002_auto_20181101_0941'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='ebooks',
            name='publishdate',
            field=models.DateField(default=''),
        ),
        migrations.AddField(
            model_name='ebooks',
            name='tags',
            field=models.ManyToManyField(to='rapp.Tag'),
        ),
    ]
