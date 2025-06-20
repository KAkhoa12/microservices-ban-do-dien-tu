# Generated by Django 5.1.7 on 2025-04-11 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0005_congtrinhtoandien_short_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='congtrinhtoandien',
            old_name='short_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='giaiphapamthanh',
            old_name='short_description',
            new_name='description',
        ),
        migrations.RemoveField(
            model_name='congtrinhtoandien',
            name='type',
        ),
        migrations.RemoveField(
            model_name='giaiphapamthanh',
            name='type',
        ),
        migrations.AlterField(
            model_name='congtrinhtoandien',
            name='image_url',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='giaiphapamthanh',
            name='image_url',
            field=models.TextField(default=''),
        ),
    ]
