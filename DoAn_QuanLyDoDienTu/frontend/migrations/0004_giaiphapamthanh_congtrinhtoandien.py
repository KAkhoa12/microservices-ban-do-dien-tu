# Generated by Django 4.2.2 on 2025-04-04 03:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0003_momopayment'),
    ]

    operations = [
        migrations.CreateModel(
            name='GiaiPhapAmThanh',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('image_url', models.TextField()),
                ('content', models.TextField()),
                ('youtube_url', models.URLField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontend.user')),
            ],
        ),
        migrations.CreateModel(
            name='CongTrinhToanDien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('image_url', models.TextField()),
                ('content', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontend.user')),
            ],
        ),
    ]
