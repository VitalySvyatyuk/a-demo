# -*- coding: utf-8 -*-
import os

from annoying.decorators import signals
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, activate
from django.utils.translation import ugettext_lazy as _

from profiles.models import UserProfile
from currencies import currencies
from issuetracker.notifications import send_issue_notification as notice
from issuetracker.signals import issue_changed
from notification import models as notification
from platforms.models import TradingAccount
from project.validators import allow_file_extensions, allow_file_size
from shared.models import StateSavingModel
from shared.utils import get_admin_url
from shared.utils import upload_to, work_days_since_now

ISSUE_STATUSES = (
    ("open", _("New issue")),
    ("rejected", _("Issue status rejected")),
    ("done", _("Answer received")),
    ("processing", _("In process")),
    ("closed", _("Issue closed")),
)

INTERNAL_TRANSFER_CURRENCY_CHOICES = (
    (True, _("In SENDER'S currency")),
    (False, _("In RECEIVER'S currency")),
)


class GenericIssue(StateSavingModel):
    status = models.CharField(_("status"), max_length=50,
                              choices=ISSUE_STATUSES, default="open")
    author = models.ForeignKey(User, related_name="created_issues",
                               verbose_name=_("author"))
    assignee = models.ForeignKey(User, blank=True, null=True,
                                 related_name="assigned_issues", verbose_name=_("assignee"))
    department = models.ForeignKey(Group,
                                   verbose_name=_("department"), null=True, blank=True)
    creation_ts = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_("creation timestamp"))
    update_ts = models.DateTimeField(auto_now=True,
                                     verbose_name=_("update timestamp"))
    deadline = models.DateField(blank=True, null=True,
                                verbose_name=_("deadline"))
    title = models.CharField(_("title"), max_length=160)
    text = models.TextField(_("text"), blank=False)
    internal_description = models.TextField(_("Internal description"), blank=True,
                                            help_text="Client does not see that field")
    internal_comment = models.TextField(_("Internal comment"), blank=True,
                                        help_text=_("Not shown to client"), default="")

    state_ignore_fields = ("update_ts", "internal_comment")  # See a note in shared/models.py.
    notifications = {
        'on_create': ('assignee',),
        'on_complete': ('assignee',),
    }

    @classmethod
    def notice_type(cls):
        """
        Returns a notice type string for a given issue class.
        """

        notice_type = cls.__name__.lower()
        return "%s_issue" % notice_type[:notice_type.rfind("issue")]

    class Meta:
        ordering = ["-creation_ts"]
        verbose_name = _("issue")
        verbose_name_plural = _("issues")

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.deadline:
            self.deadline = self.get_default_deadline()
        if not self.title:
            self.title = self.generate_title()
        if not self.text:
            self.text = self.generate_text()
        if not self.internal_description:
            self.internal_description = self.generate_internal_description()
        changes = self._get_changes()
        if changes:
            issue_changed.send(sender=self.__class__,
                               changes=changes,
                               old_instance=self._initial_instance,
                               instance=self)
        return super(GenericIssue, self).save(*args, **kwargs)

    def get_admin_url(self):
        return get_admin_url(self)

    def get_default_deadline(self):
        return work_days_since_now(3).date()

    def generate_title(self):
        """This should be overriden in subclasses."""
        return self.title

    def generate_text(self):
        """This should be overriden in subclasses."""
        return self.text

    def generate_internal_description(self):
        """This should be overriden in subclasses."""
        return self.internal_description


class IssueComment(models.Model):
    issue = models.ForeignKey(GenericIssue,
                              related_name="comments", verbose_name=_("issue"))
    user = models.ForeignKey(User, verbose_name=_("user"))
    text = models.TextField(_("comment text"))
    creation_ts = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_("creation timestamp"))

    def __unicode__(self):
        return unicode(self.creation_ts)

    class Meta:
        verbose_name = _("issue comment")
        verbose_name_plural = _("issue comments")
        get_latest_by = "creation_ts"


class IssueChangeHistory(models.Model):
    issue = models.ForeignKey(GenericIssue)
    creation_ts = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_("creation timestamp"))
    user = models.ForeignKey(User, verbose_name=_("change initiator"))
    text = models.TextField(_("change description"))


class IssueAttachment(models.Model):
    issue = models.ForeignKey(GenericIssue,
                              related_name="attachments", verbose_name=_("issue"))
    user = models.ForeignKey(User, verbose_name=_("user"))

    EXTENSIONS = 'doc', 'docx', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pdf', 'xls', 'xlsx'
    FILESIZE_LIMIT = 1024 ** 2 * 5
    FILE_HELP_TEXT = _('Supported extensions: %(ext)s. Filesize limit: %(limit)s Mb') % {
        'ext': ', '.join(EXTENSIONS),
        'limit': '%.2f' % (FILESIZE_LIMIT / 1024.0 / 1024)
    }
    file = models.FileField(
        _("Attachment"),
        upload_to=upload_to("issue_attachments"),
        help_text=FILE_HELP_TEXT,
        validators=[
            allow_file_extensions(EXTENSIONS),
            allow_file_size(FILESIZE_LIMIT)
        ]
    )

    class Meta:
        verbose_name = _("issue attachment")
        verbose_name_plural = _("issue attachment")

    def __unicode__(self):
        try:
            return os.path.basename(self.file.name)
        except AttributeError:
            return _("<unknown file>")


# Specific issue types
class CheckDocumentIssue(GenericIssue):
    document = models.ForeignKey("profiles.UserDocument",
                                 verbose_name=_("document"))

    class Meta:
        verbose_name = _("check document issue")
        verbose_name_plural = _("check document issues")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.author = self.document.user
            self.department = Group.objects.get(name="Back office")
            self.status = "open"

        super(CheckDocumentIssue, self).save(*args, **kwargs)

    def generate_text(self):
        return _('Set profile fields as "approved"')

    def generate_title(self):
        return _("Check validity of %s of user %s") % \
               (self.document.name, self.author)


class ApproveOpenECNIssue(GenericIssue):

    allow_open_invest = models.BooleanField(_('Can open ECN.Invest accounts'), default=False)

    class Meta:
        verbose_name = _("Approve open ECN.Invest account")
        verbose_name_plural = _("Approves open ECN.Invest account")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.department = Group.objects.get(name="Back office")
        super(ApproveOpenECNIssue, self).save(*args, **kwargs)
        UserProfile.objects.filter(user=self.author).update(allow_open_invest=self.allow_open_invest)


    def generate_text(self):
        return _('Enable ability to open ECN.Invest accounts')

    def generate_title(self):
        return _("Check validity user %s") % self.author


class RestoreFromArchiveIssue(GenericIssue):
    account = models.ForeignKey("platforms.TradingAccount", verbose_name=_("account"))

    notifications = {
        'on_create': ('assignee', 'author'),
        'on_complete': ('author',),
    }

    class Meta:
        verbose_name = _("restore account from archive issue")
        verbose_name_plural = _("restore account from archive issue")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.author = self.account.user
            # self.department = Group.objects.get(name="Tech support")
            self.status = "open"
        super(RestoreFromArchiveIssue, self).save(*args, **kwargs)

    def generate_title(self):
        data = {"user": self.author,
                "account": self.account,
                }
        return _("Restore account %(account)s of user %(user)s "
                 "from archive") % data

    def generate_internal_description(self):
        return mark_safe(u"""Необходимо:
    1) Восстановить счёт из архива в MT4
    2) Снять в <a href="%s">админке сайта</a> две галочки: "Счёт удалён" и "Счёт в архиве".""" %
                         reverse("admin:mt4_mt4account_change", args=(self.account.pk,)))


class UserIssue(GenericIssue):
    notifications = {
        'on_create': ('assignee', 'author'),
        # 'on_change': ('assignee', 'author'),
        'on_complete': ('author',),
        'on_comment': ('author', 'assignee')
    }

    def save(self, *args, **kwargs):
        if not self.pk:
            self.status = "open"
            if not self.department:
                self.department = Group.objects.get(name="Portfolio management")
        super(UserIssue, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return "issuetracker_issue_detail", [self.pk]

    class Meta:
        verbose_name = _("user issue")
        verbose_name_plural = _("user issues")


CURRENCY_CHOICES = currencies.choices()


class InternalTransferIssue(GenericIssue):
    sender = models.ForeignKey("platforms.TradingAccount", verbose_name=_("sender"),
                               related_name="transfers")
    recipient = models.IntegerField(_("recipient"),
                                    validators=[MinValueValidator(0)],
                                    help_text=_("Recipient's account number."), blank=True)
    amount = models.DecimalField(_("amount"),
                                 max_digits=10, decimal_places=2,
                                 validators=[MinValueValidator(0)],
                                 help_text=_("Amount of money to transfer"))
    currency = models.CharField(_("Currency"), max_length=6, null=True, blank=True,
                                choices=CURRENCY_CHOICES, default="USD")

    notifications = {
        'on_create': ('assignee',),
        'on_complete': ('author',)
    }

    class Meta:
        verbose_name = _("internal transfer issue")
        verbose_name_plural = _("internal transfer issues")

    def generate_title(self):
        return u"Перевести деньги со счета %s на %s" % (self.sender.mt4_id,
                                                        self.recipient)

    def generate_text(self):
        # Quering MetaTrader API for recipient's details (currently, we assume
        # that we __always__ have a valid response from the API).
        try:
            recipient = TradingAccount.objects.get(mt4_id=self.recipient).user
        except TradingAccount.DoesNotExist:
            recipient = None


        current_language = get_language()
        activate('ru')  # This text is only shown to staff, so we should always use Russian


        result = u"""
            Transfer details:

            From user:
            --------
            Full name.: {issue.sender.user.first_name} {issue.sender.user.last_name} {issue.sender.user.profile.middle_name}
            City: {issue.sender.user.profile.city}
            Email: {issue.sender.user.email}
            Account: {issue.sender}
            Currency: {issue.currency}
            Amount: {issue.amount}
            """.format(
            issue=self,
        )
        if not recipient:
            result += u"Кому: {issue.recipient}".format(issue=self)
        else:
            result += u"""
            To:
            -----
            Full name: {recipient.first_name} {recipient.last_name} {recipient.profile.middle_name}
            City: {recipient.profile.city}
            Email: {recipient.email}
            Account: {account}
            """.format(recipient=recipient, account=self.recipient)
        activate(current_language)

        return result

    def save(self, *args, **kwargs):
        if not self.pk:
            self.author = self.sender.user
            self.department = Group.objects.get(name="Back office")
            self.status = "open"

        super(InternalTransferIssue, self).save(*args, **kwargs)


@signals.post_save(sender=IssueComment)
def on_comment(sender, instance, created, **kwargs):
    if isinstance(instance.issue, (UserIssue,)):
        notice_type = instance.issue.notice_type()
        notice(notice_type, event="on_comment")(
            sender=instance.user, instance=instance.issue, created=False,
            # FIXME: well, yeah, that"s kind of redundant, but I can"t
            # think of anything better right now.
            comment=instance)

    if 'status' not in instance.issue.changes:
        instance.issue.status = "processing"
    instance.issue.save()


@signals.post_save(sender=IssueAttachment)
def on_attachment(sender, instance, created, **kwargs):
    notice_type = instance.issue.notice_type()
    if instance.issue.status != 'closed':
        notice(notice_type, event="on_attachment")(
            sender=instance.user, instance=instance.issue, created=False,
            attachment=instance)


# Helpers.

def issue(**kwargs):
    """A nice shortcut for creating issues.

    Issue type is guessed from a given key-value pair, which is
    currently forced to be single.
    """
    if len(kwargs) != 1:
        raise TypeError(
            "issue() should be called with a single keyword argument")

    attr, instance = kwargs.items()[0]
    for cls in GenericIssue.__subclasses__():
        if hasattr(cls, attr):
            return cls.objects.create(**kwargs)


# Disable generic issue notifications after subclasses have been initialized

@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'issuetracker':
        return
    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(UserIssue),
        codename="can_access_all_issues")

    if created:
        permission.name = "Can view requests of all performers"
        permission.save()
        print "Adding permission: %s" % permission


class CheckOnChargebackIssue(GenericIssue):
    user_requested_check = models.BooleanField(default=False)

    class Meta:
        verbose_name = u"Проверка пользователя на chargeback"
        verbose_name_plural = u"Проверка пользователей на chargeback"

    def generate_title(self):
        return u"Проверить пользователя %s на возможность chargeback" % (self.author)

    def generate_text(self):
        return u"Проверить пользователя %s на возможность chargeback.\n" \
               u"Если документы проходят проверку поставить статус \"Запрос закрыт\" для разблокировки аккаунта.\n " \
               u"В случае НЕправильных документов: \n" \
               u"1) Добавить коментарии к задаче для пользователя;\n" \
               u"2) Поставить статус \"Отклонена\"; \n" \
               u"3) Сохранить." % (self.author)

    def save(self, *args, **kwargs):
        from platforms.models import TradingAccount
        if not self.pk:
            # self.department = Group.objects.get(name="Accounting")
            self.status = "open"
        elif self.status == "closed":
            for account in self.author.accounts.filter(last_block_reason=TradingAccount.REASON_CHARGEBACK):
                account.block(False)
            for request in self.chargeback_requests:
                if request.params.get('cardnumber') and not self.author.profile.is_card_verified(
                        request.params['cardnumber']):
                    self.author.profile.add_verified_card(request.params['cardnumber'])
            notification.send([self.author], "account_unblock")
        elif self.status == "rejected":
            finance_dep_comment = u' '.join([comment.text for comment in self.comments.all()])
            notification.send([self.author], "account_unblock_rejected", {"finance_dep_comment": finance_dep_comment})
        super(CheckOnChargebackIssue, self).save(*args, **kwargs)

    @property
    def chargeback_requests(self):
        return self.author.profile.deposit_requests.possible_chargeback() \
            .filter(params__contains='chargeback_suspect')
