# Generated by Django 3.1 on 2020-09-26 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweet', '0005_hashtag_most_popular_tweet'),
    ]

    operations = [
        migrations.AddField(
            model_name='hashtag',
            name='last_modify',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
