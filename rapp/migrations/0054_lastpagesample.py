# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-09 13:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rapp', '0053_subscriptiontry_localip'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lastpagesample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('epubcfi', models.TextField(default='')),
                ('time', models.DateTimeField(auto_now=True)),
                ('ebook', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='rapp.Ebooks')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
