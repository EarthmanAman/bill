# Generated by Django 3.2.9 on 2021-12-13 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesa_api', '0002_auto_20211207_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mpesacallbacks',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='mpesacalls',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='mpesapayment',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]