# Generated by Django 3.2 on 2021-06-18 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remindmoi_bot', '0005_alter_reminder_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reminder',
            name='stream',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AlterField(
            model_name='reminder',
            name='topic',
            field=models.CharField(default='', max_length=60),
        ),
    ]