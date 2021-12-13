# Generated by Django 3.2.9 on 2021-12-12 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_bill_units'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='units',
            field=models.CharField(default='0.0', max_length=50),
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.subscription')),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_no', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.package')),
            ],
        ),
    ]