from django.db import transaction
from sentry.models.integration import ExternalProviders
from sentry.models.notificationsetting import (
    NotificationScopeType,
    NotificationSetting,
    NotificationSettingOptionValues,
    NotificationSettingTypes,
    NotificationTargetType,
)
from sentry.models.useroption import UserOption


def validate(type: NotificationSettingTypes, value: NotificationSettingOptionValues):
    return _get_legacy_value(type, value) is not None


def _get_scope(user_id, project=None, organization=None):
    """
    TODO describe
    Figure out the scope from parameters.
    TODO Validation? Confirm that the user has permission?
    TODO this doesn't seem right, do I need to switch on type?

    :param user_id: The user's ID
    :param project: (Optional) TODO
    :param organization: (Optional) TODO

    :return: (scope_type, scope_identifier)
    """

    if project:
        return NotificationScopeType.PROJECT, project.id

    if organization:
        return NotificationScopeType.ORGANIZATION, organization.id


    return NotificationScopeType.USER, user_id


def _get_target(user_id=None, team_id=None):
    """
    TODO describe
    Figure out the target from parameters.

    :return: (target_type, target_identifier)
    """

    if user_id:
        return NotificationTargetType.USER, user_id

    if team_id:
        return NotificationTargetType.TEAM, team_id

    raise Exception("TODO")


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
    TODO once we're off UserOptions, use this dict of dicts in "validate", but
    make it a dict of sets.

    :param type: NotificationSettingTypes enum
    :param value: NotificationSettingOptionValues enum
    :return: String TODO or an int sometimes?
    """

    return (
        {
            NotificationSettingTypes.DEPLOY: {
                NotificationSettingOptionValues.ALWAYS: 2,
                NotificationSettingOptionValues.COMMITTED_ONLY: 3,
                NotificationSettingOptionValues.NEVER: 4,
            },
            NotificationSettingTypes.ISSUE_ALERTS: {
                NotificationSettingOptionValues.ALWAYS: 1,
                NotificationSettingOptionValues.NEVER: 0,
            },
            NotificationSettingTypes.WORKFLOW: {
                NotificationSettingOptionValues.ALWAYS: 0,
                NotificationSettingOptionValues.SUBSCRIBE_ONLY: 1,
                NotificationSettingOptionValues.NEVER: 2,
            },
        }
        .get(type, {})
        .get(value)
    )


class NotificationsManager:
    """
    TODO add a caching layer for notification settings
    TODO inherit from BaseManager or OptionsManager
    """

    @staticmethod
    def notify(provider: ExternalProviders, type: NotificationSettingTypes, user_id=None, team_id=None, data=None):
        """
        TODO DESCRIBE

        :param provider: ExternalProviders enum
        :param type: NotificationSettingTypes enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :param data: TODO
        :return:
        """
        pass

    @staticmethod
    def get_settings(
        provider: ExternalProviders,
        type: NotificationSettingTypes,
        user_id=None,
        team_id=None,
        project_id=None,
        organization_id=None,
    ):
        """
        TODO DESCRIBE
        TODO HANDLE not exists

        If no entry exists, this will return DEFAULT, not None.

        :param provider: ExternalProviders enum
        :param type: NotificationSetting.type enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :param project_id: Project object's ID
        :param organization_id: Organization object's ID

        :return: NotificationSettingOptionValues enum
        """
        pass

    @staticmethod
    def update_settings(
        provider: ExternalProviders,
        type: NotificationSettingTypes,
        value: NotificationSettingOptionValues,
        user_id=None,
        team_id=None,
        **kwargs,
    ):
        """
        TODO MARCOS DESCRIBE
        Scenario 1: Updating a user's org-independent preferences
        Scenario 2: Updating a user's per-project preferences
        Scenario 3: Updating a user's per-organization preferences

        :param provider: ExternalProviders enum
        :param type: NotificationSettingTypes enum
        :param value: NotificationSettingOptionValues enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :param kwargs: (deprecated) User object
        """

        kwargs = kwargs or {}
        project_option = kwargs.get("project")
        user_id_option = user_id or (kwargs.get("user") or {}).id
        team_id_option = team_id or (kwargs.get("team") or {}).id

        if not validate(type, value):
            raise Exception("TODO VALIDATE")

        scope_type, scope_identifier = _get_scope(user_id_option, project=project_option)
        target_type, target_identifier = _get_target(user_id_option, team_id_option)

        with transaction.atomic():
            setting, created = NotificationSetting.objects.get_or_create(
                scope_type=scope_type,
                scope_identifier=scope_identifier,
                target_type=target_type,
                target_identifier=target_identifier,
                provider=provider,
                type=type,
                defaults={"value": value},
            )
            if not created and setting.value != value:
                setting.update(value=value)

            UserOption.objects.set_value(
                key=_get_legacy_key(type), value=_get_legacy_value(type, value), kwargs=kwargs
            )

    @staticmethod
    def remove_settings(
        provider: ExternalProviders,
        type: NotificationSettingTypes,
        user_id=None,
        team_id=None,
        **kwargs
    ):
        """
        TODO should this delete the row or set to default?

        :param provider: ExternalProviders enum
        :param type: NotificationSettingTypes enum
        :param user_id: User object's ID
        :param team_id: Team object's ID
        :param kwargs: (deprecated) User object
        """

        kwargs = kwargs or {}
        project_option = kwargs.get("project")
        user_id_option = user_id or (kwargs.get("user") or {}).id
        team_id_option = team_id or (kwargs.get("team") or {}).id
        scope_type, scope_identifier = _get_scope(user_id_option, project=project_option)
        target_type, target_identifier = _get_target(user_id_option, team_id_option)

        with transaction.atomic():
            NotificationSetting.objects.filter(
                provider=provider,
                type=type,
                scope_type=scope_type,
                scope_identifier=scope_identifier,
                target_type=target_type,
                target_identifier=target_identifier,
            ).delete()
            UserOption.objects.unset_value(key=_get_legacy_key(type), kwargs=kwargs)

    @staticmethod
    def remove_settings_for_user():
        pass

    @staticmethod
    def remove_settings_for_team():
        pass

    @staticmethod
    def remove_settings_for_project():
        pass

    @staticmethod
    def remove_settings_for_organization():
        pass
