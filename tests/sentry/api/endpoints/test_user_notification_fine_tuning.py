from django.core.urlresolvers import reverse

from sentry.models import UserEmail, UserOption
from sentry.models.integration import ExternalProviders
from sentry.models.notificationsetting import NotificationSettingTypes, NotificationSettingOptionValues
from sentry.notifications.manager import NotificationsManager
from sentry.testutils import APITestCase


class UserNotificationFineTuningTest(APITestCase):
    endpoint = "sentry-api-0-user-notifications-fine-tuning"

    def setUp(self):
        self.user = self.create_user(email="a@example.com")
        self.org = self.create_organization(name="Org Name", owner=self.user)
        self.org2 = self.create_organization(name="Another Org", owner=self.user)
        self.team = self.create_team(name="Team Name", organization=self.org, members=[self.user])
        self.project = self.create_project(
            organization=self.org, teams=[self.team], name="Project Name"
        )

        self.project2 = self.create_project(
            organization=self.org, teams=[self.team], name="Another Name"
        )

        self.login_as(user=self.user)

    def test_returns_correct_defaults(self):
        NotificationsManager.update_settings(
            ExternalProviders.EMAIL,
            NotificationSettingTypes.ISSUE_ALERTS,
            NotificationSettingOptionValues.ALWAYS,
            user=self.user,
            project=self.project,
        )
        response = self.get_valid_response("me", "alerts")
        assert response.data.get(self.project.id) == 1

        NotificationsManager.update_settings(
            ExternalProviders.EMAIL,
            NotificationSettingTypes.DEPLOY,
            NotificationSettingOptionValues.ALWAYS,
            user=self.user,
            organization=self.org
        )
        response = self.get_valid_response("me", "deploy")
        assert response.data.get(self.org.id) == 1

        UserOption.objects.create(
            user=self.user,
            organization=None,
            key="reports:disabled-organizations",
            value=[self.org.id],
        )
        response = self.get_valid_response("me", "reports")
        assert response.data.get(self.org.id) == 0

    def test_invalid_notification_type(self):
        self.get_valid_response("me", "invalid", status_code=404)
        self.get_valid_response("me", "invalid", method="put", status_code=404)

    def test_update_invalid_project(self):
        self.get_valid_response("me", "alerts", method="put", status_code=403, **{"123": 1})

    def test_invalid_id_value(self):
        self.get_valid_response("me", "alerts", method="put", status_code=400, **{"nope": 1})

    def test_saves_and_returns_alerts(self):
        self.get_valid_response(
            "me",
            "alerts",
            method="put",
            status_code=204,
            **{self.project.id: 1, self.project2.id: 0}
        )

        assert NotificationsManager.get_settings(
            provider=ExternalProviders.EMAIL,
            type=NotificationSettingTypes.ISSUE_ALERTS,
            user_id=self.user.id,
            project_id=self.project.id,
        ) == NotificationSettingOptionValues.ALWAYS

        assert NotificationsManager.get_settings(
            provider=ExternalProviders.EMAIL,
            type=NotificationSettingTypes.ISSUE_ALERTS,
            user_id=self.user.id,
            project_id=self.project2.id,
        ) == NotificationSettingOptionValues.NEVER

        # Can return to default
        self.get_valid_response(
            "me",
            "alerts",
            method="put",
            status_code=204,
            **{self.project.id: -1}
        )

        assert NotificationsManager.get_settings(
            provider=ExternalProviders.EMAIL,
            type=NotificationSettingTypes.ISSUE_ALERTS,
            user_id=self.user.id,
            project_id=self.project.id,
        ) == NotificationSettingOptionValues.DEFAULT

        assert NotificationsManager.get_settings(
            provider=ExternalProviders.EMAIL,
            type=NotificationSettingTypes.ISSUE_ALERTS,
            user_id=self.user.id,
            project_id=self.project2.id,
        ) == NotificationSettingOptionValues.NEVER

    def test_saves_and_returns_workflow(self):
        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "workflow"},
        )

        update = {}
        update[self.project.id] = 1
        update[self.project2.id] = 2

        resp = self.client.put(url, data=update)
        assert resp.status_code == 204

        assert (
                UserOption.objects.get(
                    user=self.user, project=self.project, key="workflow:notifications"
                ).value
                == "1"
        )

        assert (
                UserOption.objects.get(
                    user=self.user, project=self.project2, key="workflow:notifications"
                ).value
                == "2"
        )

        update = {}
        update[self.project.id] = -1
        # Can return to default
        resp = self.client.put(url, data=update)
        assert resp.status_code == 204

        assert not UserOption.objects.filter(
            user=self.user, project=self.project, key="workflow:notifications"
        )

        assert (
                UserOption.objects.get(
                    user=self.user, project=self.project2, key="workflow:notifications"
                ).value
                == "2"
        )

    def test_saves_and_returns_email_routing(self):
        UserEmail.objects.create(user=self.user, email="alias@example.com", is_verified=True).save()

        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "email"},
        )

        update = {}
        update[self.project.id] = "a@example.com"
        update[self.project2.id] = "alias@example.com"

        resp = self.client.put(url, data=update)
        assert resp.status_code == 204

        assert (
                UserOption.objects.get(user=self.user, project=self.project, key="mail:email").value
                == "a@example.com"
        )

        assert (
                UserOption.objects.get(user=self.user, project=self.project2, key="mail:email").value
                == "alias@example.com"
        )

    def test_email_routing_emails_must_be_verified(self):
        UserEmail.objects.create(
            user=self.user, email="alias@example.com", is_verified=False
        ).save()

        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "email"},
        )

        update = {}
        update[self.project.id] = "alias@example.com"

        resp = self.client.put(url, data=update)
        assert resp.status_code == 400

    def test_email_routing_emails_must_be_valid(self):
        new_user = self.create_user(email="b@example.com")
        UserEmail.objects.create(user=new_user, email="alias2@example.com", is_verified=True).save()

        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "email"},
        )

        update = {}
        update[self.project2.id] = "alias2@example.com"

        resp = self.client.put(url, data=update)
        assert resp.status_code == 400

    def test_saves_and_returns_deploy(self):
        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "deploy"},
        )

        update = {}
        update[self.org.id] = 0

        resp = self.client.put(url, data=update)
        assert resp.status_code == 204

        assert (
                UserOption.objects.get(
                    user=self.user, organization=self.org.id, key="deploy-emails"
                ).value
                == "0"
        )

        update = {}
        update[self.org.id] = 1
        resp = self.client.put(url, data=update)
        assert (
                UserOption.objects.get(user=self.user, organization=self.org, key="deploy-emails").value
                == "1"
        )

        update = {}
        update[self.org.id] = -1
        resp = self.client.put(url, data=update)
        assert not UserOption.objects.filter(
            user=self.user, organization=self.org, key="deploy-emails"
        ).exists()

    def test_saves_and_returns_weekly_reports(self):
        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "reports"},
        )

        update = {}
        update[self.org.id] = 0
        update[self.org2.id] = "0"

        resp = self.client.put(url, data=update)
        assert resp.status_code == 204

        assert set(
            UserOption.objects.get(user=self.user, key="reports:disabled-organizations").value
        ) == {self.org.id, self.org2.id}

        update = {}
        update[self.org.id] = 1
        resp = self.client.put(url, data=update)
        assert set(
            UserOption.objects.get(user=self.user, key="reports:disabled-organizations").value
        ) == {self.org2.id}

        update = {}
        update[self.org.id] = 0
        resp = self.client.put(url, data=update)
        assert set(
            UserOption.objects.get(user=self.user, key="reports:disabled-organizations").value
        ) == {self.org.id, self.org2.id}

    def test_enable_weekly_reports_from_default_setting(self):
        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "reports"},
        )

        update = {}
        update[self.org.id] = 1
        update[self.org2.id] = "1"

        resp = self.client.put(url, data=update)
        assert resp.status_code == 204

        assert (
                set(UserOption.objects.get(user=self.user, key="reports:disabled-organizations").value)
                == set()
        )

        # can disable
        update = {}
        update[self.org.id] = 0
        resp = self.client.put(url, data=update)
        assert set(
            UserOption.objects.get(user=self.user, key="reports:disabled-organizations").value
        ) == {self.org.id}

        # re-enable
        update = {}
        update[self.org.id] = 1
        resp = self.client.put(url, data=update)
        assert (
                set(UserOption.objects.get(user=self.user, key="reports:disabled-organizations").value)
                == set()
        )

    def test_permissions(self):
        new_user = self.create_user(email="b@example.com")
        new_org = self.create_organization(name="New Org")
        new_team = self.create_team(name="New Team", organization=new_org, members=[new_user])
        new_project = self.create_project(
            organization=new_org, teams=[new_team], name="New Project"
        )

        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "reports"},
        )

        update = {}
        update[new_org.id] = 0

        resp = self.client.put(url, data=update)
        assert resp.status_code == 403

        assert not UserOption.objects.filter(
            user=self.user, organization=new_org, key="reports"
        ).exists()

        url = reverse(
            "sentry-api-0-user-notifications-fine-tuning",
            kwargs={"user_id": "me", "notification_type": "alerts"},
        )
        update = {}
        update[new_project.id] = 1
        resp = self.client.put(url, data=update)
        assert resp.status_code == 403

        assert not UserOption.objects.filter(
            user=self.user, project=new_project, key="mail:alert"
        ).exists()
