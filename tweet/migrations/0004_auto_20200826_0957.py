# Generated by Django 3.1 on 2020-08-26 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweet', '0003_tweet_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commentconnector',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='shareconnector',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterModelOptions(
            name='tweet',
            options={'ordering': ('-created',)},
        ),
        migrations.AlterField(
            model_name='tweet',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
