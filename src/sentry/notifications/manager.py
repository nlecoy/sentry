from sentry.models.notificationsetting import (
    NotificationSettingTypes,
    NotificationSettingOptionValues,
)
from sentry.models.useroption import UserOption


def _get_legacy_key(type: NotificationSettingTypes):
    """
    Temporary mapping from new enum types to legacy strings.

    :param type: NotificationSettingTypes enum
    :return: String
    """
    return {
        NotificationSettingTypes.DEPLOY: "deploy-emails",
        NotificationSettingTypes.ISSUE_ALERTS: "mail:alert",
        NotificationSettingTypes.WORKFLOW: "workflow:notifications",
    }.get(type)


def _get_legacy_value(type: NotificationSettingTypes, value: NotificationSettingOptionValues):
    """
    Temporary mapping from new enum types to legacy strings. Each type has a separate mapping.

    :param type: NotificationSettingTypes enum
    :param value: NotificationSettingOptionValues enum
    :return: String TODO or an int sometimes?
    """

    return (
        {
            NotificationSettingTypes.DEPLOY: {
                # TODO
            },
            NotificationSettingTypes.ISSUE_ALERTS: {
                NotificationSettingOptionValues.ALWAYS: 1,
                NotificationSettingOptionValues.NEVER: 0,
            },
            NotificationSettingTypes.WORKFLOW: {
                # TODO
            },
        }
        .get(type, {})
        .get(value)
    )


class NotificationsManager:
    """
    TODO add a caching layer for notification settings
    """

    @staticmethod
    def notify(type: NotificationSettingTypes, user_id=None, team_id=None, data=None):
        """

        :param type: NotificationSettingTypes enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :param data: TODO
        :return:
        """
        pass

    @staticmethod
    def get_settings(type: NotificationSettingTypes, user_id=None, team_id=None):
        """
        :param type: NotificationSetting.type enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :return: NotificationSettingOptionValues enum
        """
        pass

    @staticmethod
    def update_settings(
        type: NotificationSettingTypes,
        value: NotificationSettingOptionValues,
        user_id=None,
        team_id=None,
        **kwargs,
    ):
        """

        :param type: NotificationSettingTypes enum
        :param value: NotificationSettingOptionValues enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :param kwargs: (deprecated) User object
        """

        UserOption.objects.set_value(
            key=_get_legacy_key(type), value=_get_legacy_value(type, value), kwargs=kwargs
        )

    @staticmethod
    def remove_settings(type: NotificationSettingTypes, user_id=None, team_id=None, **kwargs):
        """

        :param type: NotificationSettingTypes enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :param kwargs: (deprecated) User object
        """

        UserOption.objects.set_value(
            key=_get_legacy_key(type), value=_get_legacy_value(type, value), kwargs=kwargs
        )
