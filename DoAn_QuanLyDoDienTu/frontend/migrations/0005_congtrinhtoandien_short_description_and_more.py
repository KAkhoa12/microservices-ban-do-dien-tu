# Generated by Django 5.1.7 on 2025-04-11 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_giaiphapamthanh_congtrinhtoandien'),
    ]

    operations = [
        migrations.AddField(
            model_name='congtrinhtoandien',
            name='short_description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='congtrinhtoandien',
            name='status',
            field=models.CharField(default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='congtrinhtoandien',
            name='type',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='giaiphapamthanh',
            name='short_description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='giaiphapamthanh',
            name='status',
            field=models.CharField(default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='giaiphapamthanh',
            name='type',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='congtrinhtoandien',
            name='content',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='congtrinhtoandien',
            name='title',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='giaiphapamthanh',
            name='content',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='giaiphapamthanh',
            name='title',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='giaiphapamthanh',
            name='youtube_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
