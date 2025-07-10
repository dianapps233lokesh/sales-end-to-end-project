from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_myuser_updated_at_alter_otp_updated_at'),  # Replace with the actual last migration
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='myuser',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
