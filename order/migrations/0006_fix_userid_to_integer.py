from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_country_order_item_type'),  # or your latest actual migration
        ('accounts', '0001_initial'),  # adjust to match your actual accounts app migration
    ]

    operations = [
        # Convert varchar to integer
        migrations.RunSQL(
            sql="""
                ALTER TABLE order_order
                ALTER COLUMN user_id TYPE integer USING user_id::integer;
            """,
            reverse_sql="""
                ALTER TABLE order_order
                ALTER COLUMN user_id TYPE varchar;
            """
        ),
        # Add foreign key constraint to accounts_myuser(id)
        migrations.RunSQL(
            sql="""
                ALTER TABLE order_order
                ADD CONSTRAINT order_order_user_id_fkey
                FOREIGN KEY (user_id) REFERENCES accounts_myuser(id) DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE order_order
                DROP CONSTRAINT order_order_user_id_fkey;
            """
        )
    ]
