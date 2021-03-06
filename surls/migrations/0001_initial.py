# Generated by Django 3.2.3 on 2021-05-18 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Surl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(db_index=True, max_length=200)),
                ('url', models.CharField(max_length=1000)),
                ('title', models.CharField(max_length=1000)),
                ('hits', models.BigIntegerField(default=0)),
                ('url_hash', models.CharField(db_index=True, default='', max_length=64)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surls.domain')),
            ],
        ),
    ]
