# Generated by Django 2.2.5 on 2021-06-14 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='discountedPrice',
        ),
    ]
