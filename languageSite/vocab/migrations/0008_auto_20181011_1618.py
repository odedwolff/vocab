# Generated by Django 2.0.3 on 2018-10-11 13:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0007_auto_20180726_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sourceExpression', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocab.Expression')),
                ('targetLanguage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocab.Language')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocab.User')),
            ],
        ),
        migrations.RemoveField(
            model_name='attempt',
            name='attemptsList',
        ),
        migrations.RemoveField(
            model_name='attemptshistory',
            name='statPoint',
        ),
        migrations.RemoveField(
            model_name='statpoint',
            name='srouce_Expression',
        ),
        migrations.RemoveField(
            model_name='statpoint',
            name='target_Language',
        ),
        migrations.RemoveField(
            model_name='statpoint',
            name='user',
        ),
        migrations.DeleteModel(
            name='Attempt',
        ),
        migrations.DeleteModel(
            name='AttemptsHistory',
        ),
        migrations.DeleteModel(
            name='StatPoint',
        ),
    ]
