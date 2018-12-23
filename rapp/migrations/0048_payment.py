# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-19 14:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rapp', '0047_auto_20181218_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentid', models.CharField(max_length=40)),
                ('amount', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('ebook', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='rapp.Ebooks')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]