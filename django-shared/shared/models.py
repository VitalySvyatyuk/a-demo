# -*- coding: utf-8 -*-

from copy import copy
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.db import models
from django.utils.translation import ugettext_lazy as _

from shared.utils import get_combinations_regexp


class StateSavingModel(models.Model):
    """A model which can track it's changes.

    A dict of changed fields is available via `changes` property.
    """
    # Note: unfortunately Django doesn't allow extending the Meta
    # class, so we're forced to define this on the model level.
    state_ignore_fields = ()  # Fields to ignore when comparing state.

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """Constructor.

        Saves a copy of the original model, to check an instance for
        differences later on.
        Pass compare_to_fresh=True to make comparisons to not persisted yet model: the whole model will be marked as change.
        """
        self.compare_to_fresh = kwargs.pop('compare_to_fresh', False)
        super(StateSavingModel, self).__init__(*args, **kwargs)

        if self.pk or self.compare_to_fresh:
            self._initial_instance = copy(self)
        else:
            self._initial_instance = None

    def _get_changes(self):
        """Generates a dict of field changes since loaded from the database.

        Returns a mapping of field names to (old, new) value pairs:

        >>> profile.changes
        {'user': (<User: boris>, <User: iggy>)}
        """
        changes = {}
        if not self._initial_instance and not self.compare_to_fresh:
            return changes  # No initial instance? Nothing to compare to.

        for field in (field.name for field in self._meta.fields
                      if field.name not in self.state_ignore_fields):
            new = getattr(self, field, None)
            old = getattr(self._initial_instance, field, None)

            if old != new:
                changes[field] = (old, new)
        return changes

    changes = property(_get_changes)

    def refresh_state(self):
        self._initial_instance = copy(self)

    def save(self, refresh_state=True, *args, **kwargs):
        result = super(StateSavingModel, self).save(*args, **kwargs)
        if refresh_state:
            self.refresh_state()
        return result


class CustomManagerMixin(object):

    # нужно для того, чтобы не переопределять методы из QuerySet в Manager
    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            if "__" not in attr:
                queryset = self.get_queryset()
                if hasattr(queryset, attr):
                    return getattr(queryset, attr, *args)
            raise


class RegexpQuerySet(QuerySet):

    def _get_all_names(self):
        result = []
        for obj in self:
            for field in self.model.objects.field_names:
                value = getattr(obj, field, None)
                if value and isinstance(value, basestring):
                    result.append(value)
        return result

    def get_regexp(self):
        return '|'.join(self._get_all_names())

    def get_combinations_regexp(self):
        return get_combinations_regexp(self._get_all_names())


class RegexpManager(models.Manager, CustomManagerMixin):
    """See "get_combinations_regexp" docstring"""

    def __init__(self):
        self.field_names = ("name", "name_en")
        super(RegexpManager, self).__init__()

    def get_queryset(self):
        return RegexpQuerySet(self.model, using=self._db)


class VideoStat(models.Model):
    '''
    Model to save video view stats.
    Works with video added using 'flowplayer' tamplatetag
    '''
    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             null=True, blank=True)
    videofile = models.CharField(_('Video file'),max_length=2048)
    timestamp = models.DateTimeField(_('Access time'),auto_now_add=True)
