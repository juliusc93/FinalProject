# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twreferences', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('place_id', models.CharField(max_length=16, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='tweet',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='twreferences.Place', null=True),
        ),
    ]
