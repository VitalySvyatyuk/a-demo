from django.dispatch import Signal

issue_changed = Signal(providing_args=['fields', 'old_instance',
    'instance'])