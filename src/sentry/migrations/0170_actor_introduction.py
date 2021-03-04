# Generated by Django 1.11.29 on 2021-03-03 22:11

from django.db import migrations, models
import django.db.models.deletion
import sentry.db.models.fields.bounded
import sentry.db.models.fields.foreignkey
import sentry.models.actor


class Migration(migrations.Migration):
    # This flag is used to mark that a migration shouldn't be automatically run in
    # production. We set this to True for operations that we think are risky and want
    # someone from ops to run manually and monitor.
    # General advice is that if in doubt, mark your migration as `is_dangerous`.
    # Some things you should always mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that
    #   they can be monitored. Since data migrations will now hold a transaction open
    #   this is even more important.
    # - Adding columns to highly active tables, even ones that are NULL.
    is_dangerous = False

    # This flag is used to decide whether to run this migration in a transaction or not.
    # By default we prefer to run in a transaction, but for migrations where you want
    # to `CREATE INDEX CONCURRENTLY` this needs to be set to False. Typically you'll
    # want to create an index concurrently when adding one to an existing table.
    # You'll also usually want to set this to `False` if you're writing a data
    # migration, since we don't want the entire migration to run in one long-running
    # transaction.
    atomic = False

    dependencies = [
        ("sentry", "0169_delete_organization_integration_from_projectcodeowners"),
    ]

    operations = [
        migrations.CreateModel(
            name="Actor",
            fields=[
                (
                    "id",
                    sentry.db.models.fields.bounded.BoundedBigAutoField(
                        primary_key=True, serialize=False
                    ),
                ),
                (
                    "type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (sentry.models.actor.ActorType(0), "team"),
                            (sentry.models.actor.ActorType(1), "user"),
                        ]
                    ),
                ),
            ],
            options={
                "db_table": "sentry_actor",
            },
        ),
        migrations.AddField(
            model_name="team",
            name="actor",
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="sentry.Actor",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="actor",
            field=sentry.db.models.fields.foreignkey.FlexibleForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="sentry.Actor",
            ),
        ),
        migrations.RunSQL(
            """
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS sentry_team_actor_idx ON sentry_team (actor_id)
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS sentry_team_actor_idx;
            """,
        ),
        migrations.RunSQL(
            """
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS auth_user_actor_idx ON auth_user (actor_id)
            """,
            reverse_sql="""
            DROP INDEX CONCURRENTLY IF EXISTS auth_user_actor_idx;
            """,
        ),
    ]
