# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-03-26 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instituto', '0012_auto_20170326_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='foto',
            field=models.ImageField(blank=True, upload_to='fotografias/'),
        ),
    ]
