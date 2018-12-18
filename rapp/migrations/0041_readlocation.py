# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-17 12:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0040_auto_20181217_1040'),
    ]

    operations = [
        migrations.CreateModel(
            name='Readlocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.IntegerField()),
                ('phase', models.CharField(choices=[('full', 'full'), ('left', 'left'), ('right', 'right')], default='full', max_length=10)),
                ('readmodel', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='rapp.Percentageread')),
            ],
        ),
    ]
