from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template import Template
from django.template.response import TemplateResponse

import notification

def view_notification(request, notification_id):
	noti = get_object_or_404(notification.models.Notification, pk=notification_id)
	return HttpResponse(noti.preview(parent=notification_id))