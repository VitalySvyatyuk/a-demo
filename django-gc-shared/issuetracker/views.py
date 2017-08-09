# -*- coding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

from annoying.decorators import render_to
import json

from issuetracker.forms import (
    UserIssueForm, FilterIssuesForm, IssueCommentForm, IssueAttachmentForm
)
from issuetracker.models import UserIssue


@permission_required('issuetracker.change_userissue')
@render_to('admin/issuetracker/dashboard_statistics.html')
def statistics_dashboard(request):
    return {}


@permission_required('issuetracker.change_userissue')
def get_statistics(request):
    from django.contrib.admin.models import ContentType
    from issuetracker.models import CheckDocumentIssue, UserIssue
    from datetime import datetime, timedelta
    from django.contrib.admin.models import LogEntry
    from django.db.models import Count

    st_type = request.GET.get('st_type')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if None in (st_type, from_date, to_date):
        return HttpResponseNotFound(json.dumps({'details': 'wrong parameters'}))

    from_date = datetime.strptime(from_date, "%d.%m.%Y")
    to_date = datetime.strptime(to_date, "%d.%m.%Y") + timedelta(hours=23, minutes=59)

    if st_type == 'queries':
        result = LogEntry.objects.filter(content_type=ContentType.objects.get_for_model(UserIssue),
                                         action_time__range=(from_date, to_date)).order_by('user').values(
            'user__first_name', 'user__last_name', 'user').annotate(count=Count('object_id', distinct=True))
    elif st_type == 'docs':
        result = LogEntry.objects.filter(content_type=ContentType.objects.get_for_model(CheckDocumentIssue),
                                         action_time__range=(from_date, to_date)).order_by('user').values(
            'user', 'user__first_name', 'user__last_name').annotate(count=Count('object_id', distinct=True))
    else:
        return HttpResponseNotFound(json.dumps({'details': 'wrong parameters'}))

    return HttpResponse(json.dumps(list(result)))


@login_required
@render_to('issuetracker/issue_create.html')
def issue_create(request):
    """fields
    Title - Create Issue
    Форма. Поля Subject, Message, File (присоединить файл)
    Создает issue, assignee - персональный менеджер
    """
    form = UserIssueForm(request.POST or None, request.FILES or None)
    response = {'form': form}

    if form.is_valid():
        issue = form.save(author=request.user)
        messages.success(request, _('Issue #%s created') % issue.pk)
        return redirect('issuetracker_issue_list')
    if request.is_ajax():
        response['TEMPLATE'] = 'issuetracker/issue_create_via_ajax.html'
    return response


@login_required
@render_to('issuetracker/user_issue_list.html')
def user_issue_list(request):
    """в меню "Client support", на русском "Поддержка")
    Показывает список UserIssue пользователя (author=request.user).
    Вид списка - таблица - поля "id, created on, status, subject").
    Внизу под таблицей ссылка на issue_create.
    Вверху фильтр по дате создания и статусу.
    Id кликабелен, ведет на вьюху issue_detail
    """
    issues = UserIssue.objects.filter(author=request.user)

    if request.method=='POST':
        filter = FilterIssuesForm(data=request.POST.copy())
        if filter.is_valid():
            status = filter.cleaned_data['status']
            from_date = filter.cleaned_data['from_date']
            to_date = filter.cleaned_data['to_date']

            if status and status != 'all':
                issues = issues.filter(status__iexact=status)
            if from_date:
                issues = issues.filter(creation_ts__gte=from_date)
            if to_date:
                issues = issues.filter(creation_ts__lte=to_date)
    else:
        filter = FilterIssuesForm()
    response = {'issues':issues, 'filter':filter}
    if request.is_ajax():
        response['TEMPLATE'] = 'issuetracker/includes/issue_list.html'
    return response


@login_required
@render_to('issuetracker/issue_detail.html')
def issue_detail(request, issue_id):
    """Показывет id, created on, status, subject, message,
    все коментарии и присоединенные файлы.
    Позволяет присоединить коментарий или файл."""
    issue = get_object_or_404(
        UserIssue.objects.filter(author=request.user), id=issue_id
    )
    return {
        'issue':issue,
        'comment_form':IssueCommentForm(),
        'attachment_form':IssueAttachmentForm()
    }


@login_required
@require_POST
def add_comment(request, issue_id):
    issue = get_object_or_404(UserIssue, id=issue_id)
    form = IssueCommentForm(data=request.POST.copy())
    if form.is_valid():
        comment = form.save(user=request.user, issue=issue)
    return HttpResponseRedirect(issue.get_absolute_url())


@login_required
@require_POST
def add_attachment(request, issue_id):
    issue = get_object_or_404(UserIssue, id=issue_id)
    form = IssueAttachmentForm(files=request.FILES)
    if form.is_valid():
        attachment = form.save(user=request.user, issue=issue)
    return HttpResponseRedirect(issue.get_absolute_url())
