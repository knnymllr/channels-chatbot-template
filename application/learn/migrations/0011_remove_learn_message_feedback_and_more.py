# Generated by Django 5.0.3 on 2024-05-16 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0010_alter_learn_message_edited_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='learn_message',
            name='feedback',
        ),
        migrations.AddField(
            model_name='learn_message',
            name='user_feedback',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='learn_message',
            name='written_feedback',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='learn_message',
            name='approved',
            field=models.BooleanField(blank=True),
        ),
    ]
