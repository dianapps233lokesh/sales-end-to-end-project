# Generated by Django 5.2.4 on 2025-07-10 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_rename_otp_code_otp_otp_remove_otp_user_otp_data_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='otp',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
