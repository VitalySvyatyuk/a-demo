from os.path import join

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader
from django.template.utils import get_app_template_dirs
from django.utils._os import safe_join
from django.utils.translation import get_language


class MultilangLoader(Loader):
    """A pure copy of filesystem loader, which searches for templates in multilang folders"""
    # FIXME: maybe do smth, for this one not to violate the DRY principle?

    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs". Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """
        if not template_dirs:
            template_dirs = settings.TEMPLATE_DIRS
            template_dirs = get_app_template_dirs('templates') + template_dirs
        language = get_language()
        if language:
            lang_path = join('multilang', language)
        else:
            lang_path = None
        for template_dir in template_dirs:
            # We need specific language templates tried first, then base folder, then Russian as fallback
            for path in (lang_path, "", "multilang/ru"):
                if path is not None:
                    try:
                        yield safe_join(template_dir, path, template_name)
                    except UnicodeDecodeError:
                        # The template dir name was a bytestring that wasn't valid UTF-8.
                        raise
                    except ValueError:
                        # The joined path was located outside of this particular
                        # template_dir (it might be inside another one, so this isn't
                        # fatal).
                        pass

    def load_template_source(self, template_name, template_dirs=None):
        tried = []
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                file = open(filepath)
                try:
                    return (file.read().decode(settings.FILE_CHARSET), filepath)
                finally:
                    file.close()
            except IOError:
                tried.append(filepath)
        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
        raise TemplateDoesNotExist(error_msg)
    load_template_source.is_usable = True
