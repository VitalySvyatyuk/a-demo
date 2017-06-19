# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.template import (Library, Node, Variable, VariableDoesNotExist,
                             TemplateSyntaxError)
from django.template.loader import get_template

from profiles.models import get_validation

register = Library()


class StatusNode(Node):
    def __init__(self, field, asvar=None):
        self.profile = Variable("profile")
        self.field = Variable(field)
        self.asvar = asvar

    def render(self, context):

        try:
            profile = self.profile.resolve(context)
            field = self.field.resolve(context)
        except VariableDoesNotExist:
            return u""

        # Tag doesn't render anything if:
        # a) profile object hasn't been assigned a pk yet,
        # b) nor profile neither related user don't have a value for a
        # given field.
        if not (profile.pk or
            getattr(profile, field, None) or
            getattr(profile.user, field, None)):
            return u""

        # import ipdb; ipdb.set_trace()
        validation = get_validation(profile.user, field)

        if self.asvar:
            context[self.asvar] = validation
            return u""
        else:
            context["validation"] = validation
            return get_template("includes/status.html").render(context)


def status(parser, token):
    """
    Template tag, rendering status template for a given field.
    Can be used in two forms:
        {% status field.name %}
    which renders `includes/status.html` template, or
        {% status field.name as var %}
    which puts validation object for a given field name into a
    variable with a given name.
    """
    bits = token.split_contents()
    tag_name = bits.pop(0)

    if not bits:
        raise TemplateSyntaxError("%r takes at least one argument"
                                  "(field name)" % tag_name)
    elif len(bits) == 3 and "as" not in bits:
        raise TemplateSyntaxError("'as' keyword missing in '%s'")

    try:
        bits.remove("as")
    except ValueError:
        pass # We don't care if `as` part is not there.
    finally:
        return StatusNode(*bits)


def has_group(obj, group):
    if isinstance(obj, User):
        return obj.profile.has_group(group)
    raise TemplateSyntaxError("has_group can only be applied to User instances")


register.filter(has_group)
register.tag(status)


@register.inclusion_tag("profiles/profile_todo_list.html")
def show_todo_list(user):
    profile = user.profile
    filled_out_address = bool(profile.city and profile.state and profile.country and profile.address)
    verified_email = bool(user.profile.email_verified)
    verified_phone = bool(get_validation(user, "phone_mobile"))
    uploaded_document = bool(user.documents.active().exists())
    percent_complete = 25 * (filled_out_address + verified_email + verified_phone + uploaded_document)
    return {
        "filled_out_address": filled_out_address,
        "verified_email": verified_email,
        "verified_phone": verified_phone,
        "uploaded_document": uploaded_document,
        "percent_complete": percent_complete,
    }
