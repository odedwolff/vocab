# Generated by Django 2.0.3 on 2018-06-04 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0003_attempt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]