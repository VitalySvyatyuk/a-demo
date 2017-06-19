# -*- coding: utf-8 -*-

# disable dirty logs in django.log
import logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

#
# @task(backend=CacheBackend(default_app), time_limit=120)
# def update_free_customers_count(user, cache_key, async=True):
#     from profiles.models import UserProfile
#     lock_cache_key = cache_key + "_lock"
#     # If the task was launched asynchronously, we will check if a lock is set to prevent
#     # two identical tasks from running at the same time
#     if async and cache.get(lock_cache_key):
#         return
#     else:
#         cache.set(lock_cache_key, True, 120)
#     free_real = UserProfile.objects.crm_unassigned_customers(user, "real").count()
#     free_demo = UserProfile.objects.crm_unassigned_customers(user, "demo").count()
#     free_empty = UserProfile.objects.crm_unassigned_customers(user, "empty").count()
#     free_ib = UserProfile.objects.crm_unassigned_customers(user, "ib").count()
#     free_for_date = datetime.now()
#     # Caching for a week, we want CRM to work FAST
#     cache.set(cache_key, [free_real, free_demo, free_empty, free_ib, free_for_date], 604800)
#     return free_real, free_demo, free_empty, free_ib, free_for_date
