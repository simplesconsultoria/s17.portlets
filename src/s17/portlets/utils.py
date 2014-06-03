# -*- coding: utf-8 -*-
from plone import api
from s17.portlets.config import HAS_PERSON

# BBB: OrderedDict drop-in substitute that works in Python 2.6
try:
    import collections
    OrderedDict = collections.OrderedDict
except AttributeError:
    import ordereddict
    OrderedDict = ordereddict.OrderedDict


def get_portrait_url(user):
    """Return the URL of the portrait on a user profile or Person object.

    :param user: [required] Userid or person object we want to get the
        portrait URL.
    :type userid: string or Person object
    :returns: URL to user portrait
    :rtype: string
    """
    if isinstance(user, str):
        membership = api.portal.get_tool('portal_membership')
        portrait = membership.getPersonalPortrait(user)
        return portrait.absolute_url()
    elif HAS_PERSON:
        assert user.portal_type == 'Person'
        if user.picture is not None:
            scales = user.restrictedTraverse('@@images')
            icon = scales.scale('picture', width=75, height=75)
            return icon.url
        else:
            return api.portal.get().absolute_url() + '/defaultUser.png'


def sort_birthdays(birthdays):
    """Return the list of birthdays sorted by day and fullname.

    Birthday items include the following information:
    - birthday: day and month
    - fullname: full name of the person
    - description: description of the person
    - url: absolute url of the Person object
    - portrait: absolute url of the person portrait

    :param birthdays: [required] list of dictionaries
    :type birthdays: list of dict
    :returns: ordered dict with dates as keys and list of birthday items as
        values
    :rtype: OrderedDict instance
    """
    def cooked_date(info):
        """Return the cooked date from the item."""
        day, month = info[0].split('/')
        return '{0}{1}'.format(month, day)

    results = {}
    for b in birthdays:
        day, info = b['birthday'], b
        if results.get(day):
            results[day] += [info]
        else:
            results[day] = [info]
        # on each day, sort info by fullname
        results[day].sort(key=lambda i: i['fullname'])

    return OrderedDict(sorted(results.items(), key=cooked_date))
