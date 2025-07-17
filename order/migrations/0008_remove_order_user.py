from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_alter_order_order_id'),  # adjust if different
        ('accounts', '0011_alter_myuser_is_active'),
    ]

    operations = [
        # Drop conflicting index
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS order_order_user_id_like;",
            reverse_sql="-- noop"
        ),
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
        # Add back the ForeignKey constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE order_order
                ADD CONSTRAINT order_order_user_id_fkey
                FOREIGN KEY (user_id)
                REFERENCES accounts_myuser(id)
                ON DELETE CASCADE;
            """,
            reverse_sql="""
                ALTER TABLE order_order
                DROP CONSTRAINT IF EXISTS order_order_user_id_fkey;
            """
        )
    ]
