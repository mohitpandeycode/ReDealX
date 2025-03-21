# Generated by Django 5.1.6 on 2025-03-20 17:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0006_alter_product_seller_alter_productimages_product_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_chats', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='home.product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_chats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('product', 'buyer', 'seller')},
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='Chat.chat')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
