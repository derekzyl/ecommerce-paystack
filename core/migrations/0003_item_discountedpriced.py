# Generated by Django 2.2.5 on 2021-06-14 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_item_discountedprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='discountedPriced',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]