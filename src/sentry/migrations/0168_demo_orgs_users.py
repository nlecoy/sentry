# Generated by Django 1.11.29 on 2021-03-02 00:45

import bitfield.models
from django.db import migrations


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
    atomic = True

    dependencies = [
        ("sentry", "0167_rm_organization_integration_from_projectcodeowners"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="flags",
            field=bitfield.models.BitField(
                (
                    (
                        "allow_joinleave",
                        "Allow members to join and leave teams without requiring approval.",
                    ),
                    (
                        "enhanced_privacy",
                        "Enable enhanced privacy controls to limit personally identifiable information (PII) as well as source code in things like notifications.",
                    ),
                    (
                        "disable_shared_issues",
                        "Disable sharing of limited details on issues to anonymous users.",
                    ),
                    (
                        "early_adopter",
                        "Enable early adopter status, gaining access to features prior to public release.",
                    ),
                    (
                        "require_2fa",
                        "Require and enforce two-factor authentication for all members.",
                    ),
                    (
                        "disable_new_visibility_features",
                        "Temporarily opt out of new visibility features and ui",
                    ),
                    ("demo_mode", "Mark an organization as a demo org."),
                ),
                default=1,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="flags",
            field=bitfield.models.BitField(
                (
                    (
                        "newsletter_consent_prompt",
                        "Do we need to ask this user for newsletter consent?",
                    ),
                    ("demo_mode", "Mark an user as a demo user."),
                ),
                default=0,
                null=True,
            ),
        ),
    ]
