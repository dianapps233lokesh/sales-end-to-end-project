from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20250710_1657'),  # Replace with the actual last migration
    ]

    operations = [
        
        migrations.AddField(
            model_name='otp',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
