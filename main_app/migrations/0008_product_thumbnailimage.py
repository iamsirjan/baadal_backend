# Generated by Django 4.0 on 2022-12-26 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_remove_product_product_image_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='thumbnailimage',
            field=models.ImageField(default='', upload_to='product/thumbnail'),
        ),
    ]
