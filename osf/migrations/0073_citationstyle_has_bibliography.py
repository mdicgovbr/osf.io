# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-04 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0072_merge_20171128_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='citationstyle',
            name='has_bibliography',
            field=models.BooleanField(default=False),
        ),
    ]
