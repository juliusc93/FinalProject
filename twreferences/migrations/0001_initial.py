# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('place_id', models.CharField(max_length=16, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('kind', models.CharField(max_length=30)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='twreferences.Place', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('userid', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('screen_name', models.CharField(max_length=30)),
                ('is_candidate', models.BooleanField(default=False)),
                ('related_to', models.ForeignKey(blank=True, to='twreferences.User', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tweet',
            name='user',
            field=models.ForeignKey(to='twreferences.User'),
        ),
    ]
