# Generated by Django 2.0.3 on 2018-07-26 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0005_user_passhash'),
    ]

    operations = [
        migrations.AddField(
            model_name='expression',
            name='frequency',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
