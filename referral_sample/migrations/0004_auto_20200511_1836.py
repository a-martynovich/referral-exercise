# Generated by Django 3.0.5 on 2020-05-11 18:36

from django.db import migrations, models
import referral_sample.models


class Migration(migrations.Migration):

    dependencies = [
        ('referral_sample', '0003_auto_20200511_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='token',
            field=models.CharField(db_index=True, default=referral_sample.models.random_token, max_length=32),
        ),
    ]
