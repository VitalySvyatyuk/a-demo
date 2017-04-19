# -*- coding: utf-8 -*-

import operator

from notification import models as notification

def send_issue_notification(label, event=None):
    """Sends a notification of a given type.

    If event argument is present, notification recipient are updated
    with values from EVENT_TYPES.
    """
    def inner(sender, instance, created, **kwargs):
        def recipients_for(event):
            """Returns a list of recipients for a given event."""
            # FIXME(Sergei): well, this is more of a hack, but it's still
            # better then explicitly listing on_comment and on_attachment
            # for each item in ISSUE_TYPES.
            if event in ('on_comment', 'on_attachment'):
                event_listeners = ('author', 'assignee')
            else:
                event_listeners = instance.notifications.get(event, ())

            recipients = []

            if 'author' in event_listeners:
                recipients.append(instance.author)
            if 'assignee' in event_listeners:
                recipients.append(instance.assignee)

            if 'department' in event_listeners and instance.department:
                recipients.extend(instance.department.user_set.all())
            return set(filter(operator.truth, recipients))

        # If event is not provided explicitly, trying to guess it from
        # other arguments.
        #
        # Note: we're forced to use a new variable, because of the way
        # Python locals are implemented.
        if not event:
            if created:
                _event = 'on_create'
            elif instance.changes:
                _event = 'on_change'
            else:
                # Failed to guess event, no idea where to send this.
                return
        else:
            _event = event

        # Calculating a list of recipients for a given event.
        recipients = recipients_for(_event)

        # HACK: a nice little `sender` abuse, excluding sender from recipients
        # list, this is currently used for comment updates.
        # TODO: make this work with other event types (when sender is an Issue
        # class)
        try:
            recipients.remove(sender)
        except KeyError:
            pass  # No duplication in recipients list — that's fine.

        # Changes aren't relevant for newly created instances.
        changes = instance.changes if not created else None

        # FIXME(Sergei): is it possible that we have both 'on_change'
        # and 'on_complete' at the same time? it's unclear from the
        # current code if we can
        if instance.status in ('done', 'rejected', 'closed'):
            recipients.update(recipients_for('on_complete'))

        try:
            reject_comment = instance.comments.all().order_by('-creation_ts')[0]
        except IndexError:
            reject_comment = None

        kwargs.update(issue=instance,
                      created=created,
                      changes=changes,
                      event=_event,
                      reject_comment=reject_comment
                      )
        
        notification.send(recipients, label, kwargs)

    return inner
