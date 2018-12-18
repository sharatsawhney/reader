# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-18 13:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rapp', '0044_auto_20181218_1308'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectionHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publicip', models.CharField(max_length=100)),
                ('localip', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('online', 'online'), ('offline', 'offline')], default='offline', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
