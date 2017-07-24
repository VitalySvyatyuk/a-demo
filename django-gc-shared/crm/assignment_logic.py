# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q

from crm.utils import Q_or, Q_and, by_last_assigned, is_office_code, get_all_offices_agent_codes
from crm.models import RegionalOffice


###############################################################################
################ Autoassignment logic #########################################
###############################################################################
def manager_for(profile, force_assign=False):
    """Collects possible managers for user profile and return one"""
    crm_managers, forced = possible_managers_for(profile)
    if not (forced or force_assign) or not crm_managers:
        return None

    manager = by_last_assigned(crm_managers)

    if not manager:
        return

    # special logic to support special office agent codes per manager
    if (manager.reassign_agent_code_to_office
        and manager.ib_account == profile.agent_code
        and manager.office
            and manager.office.agent_code):
        # We don't need to save profile here, save will be called later
        profile.agent_code = manager.office.agent_code
    return manager.user


def possible_managers_for(profile):
    """
    Collects all available managers for this user profile
    returns
        [crm_managers]
        bool(force assignment)
    """
    if profile.registered_from:  # For now we have only magicoption.com
        usr = User.objects.get(pk=260221)  # Ivan Solovyev from Ukraine magicoption partner
        return [usr.crm_manager], False

    from crm.models import PersonalManager
    if profile.agent_code:
        # manager by code
        managers = PersonalManager.objects \
            .active() \
            .by_agent_code(profile.agent_code)
        if managers:
            return managers, True

        # office by code
        managers = RegionalOffice.objects \
            .filter(is_active=True) \
            .by_agent_code(profile.agent_code) \
            .crm_managers() \
            .active() \
            .autoassignable()
        if managers:
            # force only partners managers, not ours
            return managers, True


    # OUR OFFICE by STATE
    if profile.state:
        # skip profiles from Saint-Petersburg(school), 'cause it is local
        managers = RegionalOffice.objects \
            .exclude(slug="spb") \
            .filter(is_active=True, is_our=True, state=profile.state) \
            .crm_managers() \
            .active() \
            .autoassignable()
        if managers:
            return managers, True

    active_managers = PersonalManager.objects.active().autoassignable()

    # if client from manager by manager country_state - attach to manager
    if profile.country or profile.state:
        managers = active_managers.by_country_state(profile.country, profile.state)
        if managers:
            return managers, True

    # other clients, which we can't handle with logic above
    if profile.country and not profile.country.is_russian_language:
        return active_managers.local().by_language(profile.country.language), False
    else:
        return active_managers.local().works_with_office(), False


################ Patnership logic #############################################
def partnership_manager_for(profile):
    from crm.models import PersonalManager
    "Collects possible managers for user profile and return one"

    managers = PersonalManager.objects.active().autoassignable().partnership()

    if profile.country:
        available_manager_langs = {lang for m in managers for lang in m.language_list}
        if profile.country.language in available_manager_langs:
            managers = managers.by_language(profile.country.language)
        else:
            managers = managers.by_language("en")
    else:
        managers = managers.by_language("ru")

    manager = by_last_assigned(managers)
    return manager.user if manager else None


###############################################################################
################ Client request logic #########################################
###############################################################################
def get_base_clients_qs():
    qs = User.objects.filter(profile__manager=None, profile__ib_manager=None,
                             last_login__gt=datetime.fromtimestamp(0))
    # LOL WUT
    qs = qs.filter(profile__registered_from="")
    return qs


def possible_clients_for(manager):
    """
    Returns tuple
        user queryset
        total available users in queue
    """

    return User.objects.none(), 0


def possible_clients_queries_for(manager):
    queries = []
    if manager.office and manager.works_with_office_clients:
        queries.append(office_query(manager.office))

    queries.append(country_state_query(manager))  # append users from priority regions

    # none office means main office, which handles all
    if not manager.office or manager.office.is_our:
        queries.append(other_clients_query(manager))
    return queries


def office_query(office):
    q = None
    # search by office state
    if office.is_our and office.state:
        q = Q_or(q, Q(profile__state=office.state))

    # or by office agent codes
    if office.get_agent_codes():
        q = Q_or(q, Q(profile__agent_code__in=office.get_agent_codes()))

        office.get_agent_codes()
    assert q  # every damn office should be created properly

    # we should filter out other offices agent codes
    all_account_mt4_ids = get_all_offices_agent_codes()
    other_offices_codes = set(all_account_mt4_ids) - set(office.get_agent_codes())
    q = Q_and(q, ~Q(profile__agent_code__in=list(other_offices_codes)))
    return q


def country_state_query(manager):
    q = Q()
    q |= Q(profile__country__name_ru__in=manager.get_country_state_list())
    q |= Q(profile__state__name_ru__in=manager.get_country_state_list())
    return q


def other_clients_query(manager):
    # add conditions to queryset
    active_offices_states = RegionalOffice.objects.our().filter(
        is_active=True
    ).exclude(
        slug="spb"
    ).values_list('state', flat=True)  # регионы всех пользоователей наших офисов кроме спб

    q = ~(
        # exclude offices clients by agent codes
        Q(profile__agent_code__in=get_all_offices_agent_codes()) |

        # filter out clients by office region, excluding our school
        # so we will not exclude SPb
        Q(profile__state__in=active_offices_states)
    )

    all_regions_list = aggregate_all_regions()

    q &= Q(profile__country__language__in=manager.language_list)

    #  исключаем пользователей из регионов для которых есть менеджеры
    q &= ~Q(profile__country__name_ru__in=all_regions_list)
    q &= ~Q(profile__state__name_ru__in=all_regions_list)
    return q


def aggregate_all_regions():
    from crm.models import PersonalManager
    regions_set = set()
    all_pm_regions = PersonalManager.objects.active()\
                                    .exclude(country_state_names='', country_state_names__isnull=False)
    for pm in all_pm_regions:
        regions_set |= set(pm.get_country_state_list())
    return regions_set
