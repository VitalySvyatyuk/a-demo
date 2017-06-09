# -*- coding: utf-8 -*-
from copy import copy
import re
from django.contrib.admin.widgets import AdminTextInputWidget
from django.core.exceptions import ValidationError

from django.forms.widgets import MultiWidget, TextInput, Select, HiddenInput
from django.forms.fields import MultiValueField
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape, escape
from django.forms import CharField, ChoiceField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.utils.html import mark_safe


class SelectPhoneCode(Select):

    def render_option(self, selected_choices, option_value, option_label, is_secondary, phone_mask):
        option_value = force_unicode(option_value)
        selected_html = ''
        if option_value in selected_choices:
            if is_secondary:
                selected_html = ''
            else:
                selected_html = u' selected="selected"'
        return u'<option value="%s" data-phone-mask="%s"%s>%s</option>' % (
            escape(option_value), phone_mask, selected_html,
            conditional_escape(force_unicode(option_label))
        )

    def render_options(self, choices, selected_choices):
        from geobase.models import Country
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        countries_dict = dict((c.pk, mark_safe(
            "+%d%s( %s )" % (
                c.phone_code,
                '&nbsp;' * (8 + 2 * (3 - len(str(c.phone_code)))),
                unicode(c))
        )) for c in Country.objects.filter(pk__in=map(lambda x: x[1], self.choices)))
        self.humanize_choices = [(code, countries_dict[pk], is_secondary, phone_mask)
                                 for code, pk, is_secondary, phone_mask in self.choices]
        for option_value, option_label, is_secondary, phone_mask in self.humanize_choices:
            if isinstance(option_label, (list, tuple)):
                for option in option_label:
                    output.append(self.render_option(
                        selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                output.append(self.render_option(
                    selected_choices, option_value, option_label, is_secondary, phone_mask))
        return u'\n'.join(output)


class ChoicePhoneField(ChoiceField):
    widget = SelectPhoneCode
    default_error_messages = {
        'invalid_choice': _(u'Select a valid choice. %(value)s is not one of the available choices.'),
    }

    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        super(ChoicePhoneField, self).validate(value)
        if value and not self.valid_value(value):
            raise ValidationError(self.error_messages[
                                  'invalid_choice'] % {'value': value})

    def valid_value(self, value):
        """
        Check to see if the provided value is a valid choice
        """
        for k, v, j, f in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == smart_unicode(k2):
                        return True
            else:
                if value == smart_unicode(k):
                    return True
        return False


def split_phone_number(phone):
    from geobase.models import Country
    if not phone:
        return None, None, None
    digits = "".join(c for c in phone if c in '1234567890')

    # Kazakhstan is a special case, because it in fact has two phone codes: +76 and +77,
    # but the people living there are accustomed to it being written as just +7
    if digits[:2] in ('76', '77'):
        return '+7', digits[1:], Country.objects.get(code="KZ")

    # General idea is to find country, which has longest match
    # by phone in phone_code field. So, if we have country with 7 and 72 codes
    # we should match the one with 72.
    # So, we sort it descending by phone_code, so longest will be first.
    # Then contatinate each country phone_code with '%' to use it as rvalue in LIKE:
    #     '79214357187' LIKE '7%' == True
    country = Country.objects.extra(
        where=["%s LIKE (phone_code::text || '%%')"],
        params=[digits]
    ).order_by('-phone_code', '-is_primary').first()
    if not country:
        return None, None, None
    return '+' + str(country.phone_code), digits[len(str(country.phone_code)):], country


class CountryPhoneCodeWidget(MultiWidget):
    """
     Widget for adding phone numbers are changin into 2 forms,1-select-box,2-textinput
    """

    def __init__(self, choices=None, attrs=None):
        from geobase.models import Country
        choices = choices or Country.get_phone_codes()
        widgets = (
            SelectPhoneCode(attrs={"class": "phone-select input_box__start_info", "dir": "auto"},
                            choices=choices),
            TextInput(attrs={
                      "class": "phone-input input_box__input input_box__input--has-start", "dir": "auto"})
        )
        super(CountryPhoneCodeWidget, self).__init__(widgets, attrs)

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        for i, widget in enumerate(self.widgets):
            final_attrs = self.build_attrs(attrs)
            id_ = final_attrs.get('id', None)
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            new_classes = final_attrs.pop('class', None)
            full_attrs = widget.attrs.copy()
            full_attrs.update(final_attrs)
            if new_classes:
                if 'class' in full_attrs:
                    full_attrs['class'] += ' ' + new_classes
                else:
                    full_attrs['class'] = new_classes
            output.append(widget.render(name + '_%s' %
                                        i, widget_value, full_attrs))
        return mark_safe(self.format_output(output))

    def decompress(self, value):
        if value:
            return split_phone_number(value)[:2]
        return None, None

    class Media:
        js = ('js/jquery.maskedinput-1.3.1.js',
              'js/define_id_phone_widget.js', )


class HiddenCountryPhoneCodeWidget(CountryPhoneCodeWidget):
    def __init__(self, choices=None, attrs=None):
        widgets = (
            HiddenInput(),
            HiddenInput()
        )
        # Call MultiWidget's init, skipping CountryPhoneCodeWidget
        super(CountryPhoneCodeWidget, self).__init__(widgets, attrs)


class CountryPhoneCodeFormField(MultiValueField):
    """
    Field for adding phone numbers are changin into 2 forms,1-select-box,2-textinput
    as keyword argument,it takes "countries",which can be "all","russian",and  a list of country-names
    """
    widget = CountryPhoneCodeWidget
    hidden_widget = HiddenCountryPhoneCodeWidget

    register = []
    delay_init = True

    def __init__(self, countries=None, **kwargs):
        """
        Hack for Django 1.7 compatibility: we do minimal initialisation first, and then,
        when all Apps have finished loading, do the final init (see geobase.apps)
        """
        self.kwargs = kwargs
        self.countries = countries
        self.register.append(self)
        super(CountryPhoneCodeFormField, self).__init__(widget=TextInput())
        if not self.delay_init:
            self.delayed_init()

    def delayed_init(self):
        from geobase.models import Country
        if 'max_length' in self.kwargs:
            self.kwargs.pop('max_length')

        choices = Country.get_phone_codes(self.countries)

        if self.kwargs.get('widget', CountryPhoneCodeWidget) in [CountryPhoneCodeWidget, AdminTextInputWidget]:
            widget = CountryPhoneCodeWidget(choices=choices)
            self.kwargs.update({'widget': widget})

        fields = (
            ChoicePhoneField(choices=choices),
            CharField()
        )
        super(CountryPhoneCodeFormField, self).__init__(fields, **self.kwargs)

    def compress(self, data_list):
        data_string = ''.join(data_list)
        return "".join(c for c in data_string if c in '1234567890+')

    def validate(self, value):
        if value and re.search("[^\d +)(-_]", value):
            raise ValidationError(_("Phone number should contain only digits"))
        elif self.required and split_phone_number(value) == (None, None, None):
            raise ValidationError(_("Enter your phone number"))


class CountryPhoneCodeField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def formfield(self, **kwargs):
        defaults = {'form_class': CountryPhoneCodeFormField}
        defaults.update(kwargs)
        return super(CountryPhoneCodeField, self).formfield(**defaults)
