# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-17 10:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rapp', '0038_rateduser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Percentageread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent', models.FloatField(default=0.0)),
                ('ebook', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='rapp.Ebooks')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='lastpage',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
