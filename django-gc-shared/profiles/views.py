# -*- coding: utf-8 -*-
import urllib
from datetime import datetime, timedelta

from annoying.decorators import render_to, ajax_request
from django.contrib import messages
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.auth.views import password_change as pass_change
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.http.response import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_GET, require_POST

import notification.models as notification
from issuetracker.models import CheckDocumentIssue, ApproveOpenECNIssue
from log.models import Logger, Events
from otp.views import security_check
from profiles.forms import DocumentForm, ProfileForm, EmailProfileForm, AvatarUploadForm
from profiles.models import UserProfile, UserDocument
from registration.backends import send_activation_email
from shared.generic_views import TemplateView
from shared.validators import email_re
from registration.models import RegistrationProfile

@login_required
@render_to("profiles/upload_document.html")
def upload_document(request):
    form = DocumentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        document = form.save(commit=False)
        document.user = request.user
        document.save()

        Logger(user=request.user, content_object=document,
               ip=request.META["REMOTE_ADDR"], event=Events.DOCUMENT_UPLOADED).save()

        messages.success(request, _("Successfully uploaded document %s") % document)

        return redirect(request.GET.get("next", "profiles_my"))
    return {"form": form}


@login_required
@require_GET
def profile_my(request):
    return profile_detail(request, request.user.username)


@render_to('profiles/create_profile.html')
def create_profile(request):
    """
    Create a profile for the current User, if one doesn't already
    exist.

    If the User already has a profile, as determined by
    `request.user.profile`, a redirect will be issued to the
    `profiles.views.edit_profile` view. If no profile model has
    been specified in the `AUTH_PROFILE_MODULE` setting,
    `django.contrib.auth.models.SiteProfileNotAvailable` will be
    raised.
    """
    try:
        profile_obj = request.user.profile
        return redirect("profiles_edit_profile")
    except ObjectDoesNotExist:
        pass

    form = ProfileForm(request.POST or None, request.FILES or None, request=request)
    if form.is_valid():
        profile_obj = form.save(commit=False)
        profile_obj.user = request.user
        profile_obj.save()

        if hasattr(form, "save_m2m"):
            form.save_m2m()
        return redirect("profiles_my")
    return {"form": form}


@login_required
@render_to('profiles/upload_avatar.html')
def upload_avatar(request):

    form = AvatarUploadForm(request.POST or None, request.FILES or None, instance=request.user.profile)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(request, _("Avatar was uploaded successfully"))
        return redirect("profiles_my")

    return {
        "form": form,
    }


@login_required
@render_to('profiles/edit_profile.html')
def edit_profile(request, username=None):
    """
    Edit the current User's profile.

    If the user does not already have a profile (as determined by
    User.profile), a redirect will be issued to the
    `profiles.views.create_profile` view; if no profile model
    has been specified in the `AUTH_PROFILE_MODULE` setting,
    `django.contrib.auth.models.SiteProfileNotAvailable` will be
    raised.
    """
    if username:
        # Making sure the logged in user has Managers groups.
        if not (request.user.profile.has_group("Managers") or request.user.is_superuser):
            return redirect("profiles_profile_detail", username)

        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    try:
        profile = user.profile
    except ObjectDoesNotExist:
        return redirect("profiles_create_profile")

    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile, request=request)

    if form.is_valid():

        result = security_check(request, request.user)
        if result:
            return result

        old_values = {
            "email": request.user.email,
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }

        updated_profile = form.save()

        changes = {change[0]: {"from": unicode(change[1][0]), "to": unicode(change[1][1])}
                   for change in updated_profile.changes.items()}

        for field_name in old_values.keys():
            old = old_values[field_name]
            new = form.cleaned_data[field_name]
            if new != old:
                changes[field_name] = {"from": old, "to": new}

        Logger(user=request.user, content_object=profile, ip=request.META["REMOTE_ADDR"],
               event=Events.PROFILE_CHANGED, params=changes).save()

        return redirect(request.GET.get("next") or "profiles_my")

    return {"form": form,
            "profile": profile}


@login_required
@require_GET
@render_to("profiles/profile_detail.html")
def profile_detail(request, username):
    """
    Detail view of a User's profile.

    If no profile model has been specified in the `AUTH_PROFILE_MODULE`
    setting, `django.contrib.auth.models.SiteProfileNotAvailable` will
    be raised.

    If the user has not yet created a profile, it will be created and
    the user will be redirected to `profiles.views.edit_profile`.
    """
    user = get_object_or_404(User, username=username)
    if user != request.user:
        raise Http404()
    profile, created = UserProfile.objects.get_or_create(user=user)
    if created and user == request.user:
        response = TemplateView.as_view(template_name="site_welcome.html")(request)
    else:
        extra_context = {"profile": profile}
        response = TemplateView.as_view(template_name="profiles/profile_detail.html",
                                        extra_context=extra_context)(request)
    return response


@login_required
@require_POST
@ajax_request
def confirm_field(request, username, field, status=None):
    """
    View, changing the status of a given field. Requires at least
    two arguments passed via query string: username for the user,
    who's profile field is validated and field name. Optionally status
    can be supplied which is either 't' or 'f' for True and False
    respectively.
    """
    status = {"t": True, "f": False, "c": None}[status]
    # FIXME: currently UserDataValidation objects can be mutated via
    # this view, how does it fit with our business logic?
    if not request.user.has_perm("profiles.change_userdatavalidation"):
        return HttpResponseForbidden()

    try:
        profile = UserProfile.objects.get(user__username=username)
    except (ObjectDoesNotExist, KeyError):
        return HttpResponseNotFound()

    validation, created = profile.user.validations.get_or_create(key=field)
    old_status = validation.is_valid
    validation.is_valid = status
    validation.comment = request.POST.get("comment")
    validation.save()

    Logger(user=request.user, content_object=profile,
           ip=request.META["REMOTE_ADDR"], event=Events.VALIDATION_OK,
           params={"field": field, "from": old_status, "to": status}).save()

    return {
        "status": "ok",
    }

@login_required
@render_to("profiles/edit_email.html")
def edit_email(request):
    if request.user.profile.email_verified:  # Already activated users are not allowed to change their emails
        return HttpResponseForbidden()
    email = request.user.email
    reg_profile = RegistrationProfile.objects.get(user=request.user)
    form = EmailProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            now = datetime.now()
            EMAIL_UPDATE_TIMEOUT = timedelta(seconds=(15 * 60))
            if 'confirmation_email_ts' in request.session and\
                    (now - request.session['confirmation_email_ts'] < EMAIL_UPDATE_TIMEOUT):
                messages.error(request, _("You can not change e-mail address more than once every fifteen minutes."))
            elif User.objects.filter(email__iexact=form.cleaned_data['email']).exists() and\
                    not form.cleaned_data['email'] == email:
                messages.error(request, _("E-mail you provided is already registered in our system."))
            else:
                form.save()

                # No need to reset password
                # password = User.objects.make_random_password(8)
                # user = request.user
                # user.save()
                password = "***"

                send_activation_email(request.user, password, reg_profile)

                request.session['confirmation_email_ts'] = now
                messages.success(request, _('Your e-mail successfully updated'))
                return redirect('registration_activation_complete')

    return {"form": form}


@render_to("profiles/unsubscribe_form.html")
def unsubscribe_form(request, email, signature, campaign_id):
    email = urllib.unquote(email)
    # if get_signature(email) != signature or not email_re.match(email):
    #     raise Http404
    # profile = User.objects.filter(email=email).first().profile
    # form = SubscriptionProfileForm(request.POST or None, instance=profile)

    # if form.is_valid():
    #     data = form.cleaned_data
    #     if not data['subscription']:
    #         try:
    #             campaign = Campaign.objects.get(id=campaign_id)
    #         except Campaign.DoesNotExist:
    #             pass
    #         else:
    #             campaign.unsubscribed += 1
    #             campaign.save()
    #     form.save()
    #     messages.success(request, _('Your subscription successfully updated'))

    return {"form": form}


@login_required
def password_change(request, *args, **kwargs):
    response = pass_change(request, *args, post_change_redirect=reverse("auth_password_change_done"), **kwargs)
    if request.method == "POST":
        if isinstance(response, HttpResponseRedirect):
            Logger(ip=request.META["REMOTE_ADDR"], event=Events.PASSWORD_CHANGE_OK,
                   user=request.user, content_object=request.user.profile).save()
        else:
            # user may have failed password confirmation only; not a crime
            if not request.user.check_password(request.POST["old_password"]):
                Logger(ip=request.META["REMOTE_ADDR"], event=Events.PASSWORD_CHANGE_FAIL,
                       user=request.user, content_object=request.user.profile).save()

    return response


@login_required
@ajax_request
def new_messages(request):
    return {
        'count': request.user.received_messages.filter(read_at__isnull=True, recipient_deleted_at__isnull=True).count()
    }


@permission_required("profiles.change_userdatavalidation")
@login_required
@render_to("profiles/verify_document.html")
def verify_document(request, issue_id):
    from shared.utils import log_change

    issue = get_object_or_404(CheckDocumentIssue, id=issue_id)

    if request.method == 'POST':
        pending_issues = list(CheckDocumentIssue.objects.filter(author=issue.author, status="open"))

        status = request.POST.get('status', None)
        comment = request.POST.get('comment')

        if status == 'match':
            for issue in pending_issues:
                issue.status = 'closed'
                issue.save()
                log_change(request, issue, u"Документы ожидающие проверку ОДОБРЕНЫ (в совокупности)")

            notification.send([issue.author], 'document_verified')
            issue.author.profile.make_documents_valid()

        elif status == 'nomatch':
            for issue in pending_issues:
                issue.status = 'rejected'
                issue.internal_comment += u'Reject reason writed by {}: {} \n{}\n'\
                    .format(request.user, comment, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                issue.save()
                log_change(request, issue, u"Документы ожидающие проверку ОТКЛОНЕНЫ (в совокупности)")
            notification.send([issue.author], 'documen_rejected', extra_context={'reject_message' : comment})
            issue.author.profile.make_documents_invalid()
        return redirect("admin:issuetracker_checkdocumentissue_changelist")

    return {
        'documents': issue.author.documents.all(),
        'status': issue.status
    }


@permission_required("profiles.change_userdatavalidation")
@login_required
@render_to("profiles/verify_document.html")
def watch_document(request, issue_id):

    issue = get_object_or_404(ApproveOpenECNIssue, id=issue_id)

    if request.method == 'POST':
        pending_issues = list(ApproveOpenECNIssue.objects.filter(author=issue.author, status="open"))

        status = request.POST.get('status', None)
        if status == 'match':
            for issue in pending_issues:
                issue.status = 'closed'
                issue.allow_open_invest = True
                issue.save()

            notification.send([issue.author], 'invest_approved')
            UserProfile.objects.filter(user=issue.author).update(allow_open_invest=True)

        return redirect("admin:issuetracker_approveopenecnissue_changelist")

    return {
        'documents': issue.author.documents.all(),
        'status': issue.status,
        'buttons': 'invest',
    }


@login_required
@require_POST
def reset_otp(request, profile_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    profile = get_object_or_404(UserProfile, id=profile_id)
    profile.delete_otp_devices(lost_otp=True)
    messages.add_message(request, messages.SUCCESS, u"OTP for %s successfully reset" % profile)
    return redirect('admin:profiles_userprofile_change', profile.id)


@permission_required("profiles.change_userdatavalidation")
def switch_documents_status(request, profile_id):
    reject_commentary = request.POST.get('commentary')
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        if not UserDocument.objects.filter(user_id=profile.user.id).exists():
            messages.add_message(request, messages.ERROR, u"{} must upload atleast 1 document to mark it's as verified".format(profile))
            return redirect('admin:profiles_userprofile_change', profile.id)
        if profile.status == UserProfile.VERIFIED:

            profile.make_documents_invalid()
            notification.send([profile.user], 'documen_rejected', extra_context={'reject_message': reject_commentary})
            messages.add_message(request, messages.SUCCESS, format_html(u"{} is <b>un</b>verified now".format(profile)))
        else:
            profile.make_documents_valid()
            notification.send([profile.user], 'document_verified')
            messages.add_message(request, messages.SUCCESS, format_html(u"{} is <b>verified</b> now".format(profile)))
        return redirect('admin:profiles_userprofile_change', profile.id)
