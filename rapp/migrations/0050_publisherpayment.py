# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-20 09:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0049_payment_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publisherpayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentid', models.CharField(max_length=40)),
                ('amount', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='rapp.Publishers')),
            ],
        ),
    ]