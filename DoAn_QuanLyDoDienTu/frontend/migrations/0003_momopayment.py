# Generated by Django 5.1.7 on 2025-03-29 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_cart_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='MomoPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=0, max_digits=10)),
                ('order_info', models.CharField(max_length=255)),
                ('request_id', models.CharField(max_length=50, unique=True)),
                ('transaction_id', models.CharField(blank=True, max_length=50, null=True)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('response_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
