# -*- coding: utf-8 -*-

from itertools import chain
import re
import os

from django.conf import settings
from django.db.models import Q
from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.urlresolvers import reverse, NoReverseMatch, get_script_prefix

from shared.compat import methodcaller


def get_icons():
    treemenus_icons_root = os.path.join(settings.PROJECT_ROOT,
                                        'django-shared', 'treemenus', 'static', 'treemenus', 'icons')
    try:
        for filename in os.listdir(treemenus_icons_root):
            yield (filename, filename[:-4])
    except:
        return


class MenuItem(models.Model):
    parent = models.ForeignKey('self', verbose_name=_('Parent'), null=True, blank=True)
    url = models.CharField(_('URL'), max_length=200, blank=True)
    named_url = models.CharField(_('Named URL'), max_length=200, blank=True)
    regex_url = models.CharField(_('Regex URL'), max_length=200, blank=True, null=True)
    target_blank = models.BooleanField(_('Open in blank page'), default=False, help_text=_('If checked open link in new page'))
    level = models.IntegerField(_('Level'), default=0, editable=False)
    rank = models.IntegerField(_('Rank'), default=0, editable=False)
    menu = models.ForeignKey('Menu', related_name='contained_items', verbose_name=_('Menu'),
                             null=True, blank=True, editable=False)
    caption_ru = models.CharField(_('Caption Russian'), max_length=150, null=True, blank=True)
    caption_en = models.CharField(_('Caption English'), max_length=150, null=True, blank=True)
    caption_id = models.CharField(_('Caption Indonesian '), max_length=150, null=True, blank=True)
    caption_zh_cn = models.CharField(_('Caption Chinese'), max_length=150, null=True, blank=True)
    caption_pl = models.CharField(_('Caption Polish'), max_length=150, null=True, blank=True)
    caption_pt = models.CharField(_('Caption Portuguese'), max_length=150, null=True, blank=True)
    caption_ar = models.CharField(_('Caption Arabic'), max_length=150, null=True, blank=True)
    caption_uk = models.CharField(_('Caption Ukrainian'), max_length=150, null=True, blank=True)
    caption_fa = models.CharField(_('Caption Persian'), max_length=150, null=True, blank=True)
    caption_hy = models.CharField(_('Caption Armenian'), max_length=150, null=True, blank=True)
    caption_ka = models.CharField(_('Caption Georgian'), max_length=150, null=True, blank=True)
    caption_fr = models.CharField(_('Caption French'), max_length=150, null=True, blank=True)
    caption_th = models.CharField(_('Caption Thai'), max_length=150, null=True, blank=True)

    visibility_condition = models.CharField(_('Visibility Condition'), max_length=200, null=True, blank=True)
    do_permission_check = models.BooleanField(_("Perform permission check"), default=False)
    icon = models.CharField(_('Icon'), null=True, blank=True, max_length=150, choices=get_icons())
    widget = models.CharField(_('Widget name'), max_length=150, null=True, blank=True)

    @property
    def caption(self):
        language = get_language()
        try:
            return getattr(self, 'caption_%s' % language.replace('-', '_'))
        except AttributeError:
            return

    def __unicode__(self):
        return self.caption

    def get_url(self):
        bits = self.named_url.split(" ")
        named_url, args = bits[0], bits[1:]
        args = filter(lambda a: "=" not in a, args)
        args = map(methodcaller("strip", '"'), args)
        kwargs = map(methodcaller("split", "="), filter(lambda a: "=" in a, args))
        try:
            return reverse(named_url, args=args, kwargs=kwargs)
        except NoReverseMatch:
            if self.url and self.url[0] == "/":
                return get_script_prefix().rstrip('/') + self.url
            else:
                return self.url

    def get_absolute_url(self):
        return self.get_url()

    def is_selected(self, request, include_children=True):
        if self.regex_url:
            self_selected = re.match(self.regex_url, request.path) is not None
        else:
            self_selected = self.get_url() == request.path

        if self_selected:
            return True

        if include_children:
            for child in self.menuitem_set.all():
                if child.is_selected(request):
                    return True

        return False

    def is_self_selected(self, request):
        return self.is_selected(request, include_children=False)

    def is_visible(self, request):

        language = get_language()

        # try:
        #     if self.do_permission_check:
        #         # у нод адрес прописан без слэша в начале
        #         url = self.url.lstrip("/")
        #         p = Page.objects.filter(url_alias__iexact=url, language=language)
        #         # если нашли страницу и юзер имеет доступ к странице
        #         if p.exists() and p[0].check_access(request.user):
        #             return True
        #         # если проверки не прошли, то элемент не показываем
        #         return False
        # except:
        #     # если будем падать, то хотя бы не потащим за собой все меню
        #     pass

        if not self.visibility_condition:
            return True

        try:
            visibility = eval(self.visibility_condition)
        except:
            return False

        return visibility

    def set_children(self, request):
        menus = dict([(m.id, m) for m in MenuItem.objects.all() if m.caption])

        def traverse(menu, menus, request):
            menu.all_children = sorted([m for m in menus.itervalues() if m.parent_id == menu.id],
                                       key=lambda key: key.rank)
            menu.is_self_selected = menu.is_self_selected(request)
            menu.is_selected = menu.is_selected(request)
            menu.is_visible = menu.is_visible(request)
            for m in menu.all_children:
                m.parent = menu
                traverse(m, menus, request)

            def traverse_up(menu, force_parent_expanded=False):
                if not menu:
                    return
                elif force_parent_expanded:
                    menu.expanded = True
                elif menu.is_selected:
                    force_parent_expanded = True
                    menu.expanded = True
                elif hasattr(menu, 'expanded'):
                    return
                elif not menu.all_children:
                    menu.expanded = False
                else:
                    menu.expanded = False
                    force_parent_expanded = menu.expanded
                traverse_up(menu.parent, force_parent_expanded)

            if not menu.all_children:
                traverse_up(menu)

        traverse(self, menus, request)

    def save(self, force_insert=False, **kwargs):
        from treemenus.utils import clean_ranks

        # Calculate level
        old_level = self.level
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0

        if self.pk:
            new_parent = self.parent
            old_parent = MenuItem.objects.get(pk=self.pk).parent
            if old_parent != new_parent:
                #If so, we need to recalculate the new ranks for the item and its siblings (both old and new ones).
                if new_parent:
                    clean_ranks(new_parent.children())  # Clean ranks for new siblings
                    self.rank = new_parent.children().count()
                super(MenuItem, self).save(force_insert,
                                           **kwargs)  # Save menu item in DB. It has now officially changed parent.
                if old_parent:
                    clean_ranks(old_parent.children())  # Clean ranks for old siblings
            else:
                super(MenuItem, self).save(force_insert, **kwargs)  # Save menu item in DB

        else:  # Saving the menu item for the first time (i.e creating the object)
            if self.rank:
                pass
            elif not self.has_siblings():
                # No siblings - initial rank is 0.
                self.rank = 0
            else:
                # Has siblings - initial rank is highest sibling rank plus 1.
                siblings = self.siblings().order_by('-rank')
                self.rank = siblings[0].rank + 1
            super(MenuItem, self).save(force_insert, **kwargs)

        # If level has changed, force children to refresh their own level
        if old_level != self.level:
            for child in self.children():
                child.save()  # Just saving is enough, it'll refresh its level correctly.

    def delete(self):
        from treemenus.utils import clean_ranks

        old_parent = self.parent
        super(MenuItem, self).delete()
        if old_parent:
            clean_ranks(old_parent.children())

    def caption_with_spacer(self):
        spacer = ''
        for i in range(0, self.level):
            spacer += u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        if self.level > 0:
            spacer += u'|-&nbsp;'
        return spacer + (self.caption or '')

    def get_flattened(self):
        flat_structure = [self]
        for child in self.children():
            flat_structure = chain(flat_structure, child.get_flattened())
        return flat_structure

    def siblings(self):
        if not self.parent:
            return MenuItem.objects.none()
        else:
            if not self.pk:  # If menu item not yet been saved in DB (i.e does not have a pk yet)
                return self.parent.children()
            else:
                return self.parent.children().exclude(pk=self.pk)

    def hasSiblings(self):
        import warnings

        warnings.warn('hasSiblings() is deprecated, use has_siblings() instead.', DeprecationWarning, stacklevel=2)
        return self.has_siblings()

    def has_siblings(self):
        return self.siblings().count() > 0

    def children(self):
        _children = MenuItem.objects.filter(parent=self).order_by('rank', )
        for child in _children:
            child.parent = self  # Hack to avoid unnecessary DB queries further down the track.
        return _children

    def hasChildren(self):
        import warnings

        warnings.warn('hasChildren() is deprecated, use has_children() instead.', DeprecationWarning, stacklevel=2)
        return self.has_children()

    def has_children(self):
        return self.children().count() > 0


class Menu(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    root_item = models.ForeignKey(MenuItem, related_name='is_root_item_of',
                                  verbose_name=_('Root Item'), null=True, blank=True, editable=False)

    def save(self, force_insert=False, **kwargs):
        if not self.root_item:
            root_item = MenuItem()
            root_item.caption_en = 'Root'
            root_item.caption_ru = _('Root')
            if not self.pk:  # If creating a new object (i.e does not have a pk yet)
                super(Menu, self).save(force_insert, **kwargs)  # Save, so that it gets a pk
                force_insert = False
            root_item.menu = self
            root_item.save()  # Save, so that it gets a pk
            self.root_item = root_item
        super(Menu, self).save(force_insert, **kwargs)

    def delete(self):
        if self.root_item is not None:
            self.root_item.delete()
        super(Menu, self).delete()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Menu')
        verbose_name_plural = _('Menus')
