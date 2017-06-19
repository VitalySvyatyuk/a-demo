from django.db import router
from django.db.models import Manager, Q
from django.db.models.sql import RawQuery

class AdvancedRawQuery(RawQuery):
    """RawQuery with advanced functions, helpers"""
    def values(self):
        "Similar to RawQuerySet.values(), but can w/o model"
        columns = self.get_columns()
        return [dict(zip(columns, row)) for row in self]
    def __repr__(self):
        return "<AdvancedRawQuery: %r>" % (self.sql % self.params)

class AdvancedManager(Manager):
    """Model Manager with advanced functions and helpers"""
    def raw_query(self, raw_query, params=None, *args, **kwargs):
        "Execute raw sql query and return result 'as is'. See AdvancedRawQuery for aditional functions"
        return AdvancedRawQuery(sql=raw_query, using=router.db_for_read(self.model), params=params)

    def text_search(self, text, lookup):
        """Doing search for over specified fields"""
        if not lookup:
            return self.get_queryset() #prevent errors, ye
        terms = text.split(' ') #we gonna search each work from query separately
        search_expr = Q()
        for term in terms: #mixing up terms with queries(lookups)
            for lkp in lookup:
                search_expr = search_expr | Q(**{ lkp: term })
        return self.get_queryset().filter(search_expr)
        
