import os.path
from django.conf import settings
from django.core.mail import EmailMessage as DjangoEmailMessage
from celery import shared_task
from curricula.models import Institution

def build_footer():
    inst = Institution.objects.first()
    if not inst:
        return """
        <div style="margin-top:30px;padding-top:15px;border-top:1px solid #e0e0e0;
                font-family:Arial, sans-serif;font-size:12px;color:#666;">
        <p style="margin:0;">
            <strong>mydep</strong><br>
            Mydep platform
        </p>
        <p style="margin-top:8px;">
            This is an automated message. Please do not reply directly to this email.
        </p>
        </div>
        """

    footer = f"""
    <div style="margin-top:30px;padding-top:15px;border-top:1px solid #e0e0e0;
            font-family:Arial, sans-serif;font-size:12px;color:#666;">
    <p style="margin:0;">
        <strong>mydep@{inst.short_en}</strong><br>
        {inst.title_en} - Mydep platform
    </p>
    <p style="margin-top:8px;">
        This is an automated message. Please do not reply directly to this email.
    </p>
    </div>
    """
    return footer

def build_subj_prefix():
    inst = Institution.objects.first()
    if not inst:
        return 'mydep: '
    subj = f'mydep@{inst.short_en}: '
    return subj

class gmailapi:
    """
    Compatibility wrapper class for Django SMTP email sending.
    Maintains the same interface as the old Gmail API client.
    """
    def __init__(self, token_file=None, credentials_file=None, from_ad=None):
        # Allow any arguments from the old constructor, but use Django settings as fallback
        self.from_ad = from_ad or getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hua.gr')

    def send(self, to, subject, body, attachments=[], cc=None):
        # Parse recipients into lists
        to_list = [e.strip() for e in to.split(',') if e.strip()] if isinstance(to, str) else (to or [])
        cc_list = [e.strip() for e in cc.split(',') if e.strip()] if isinstance(cc, str) and cc else (cc or [])

        email = DjangoEmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_ad,
            to=to_list,
            cc=cc_list,
        )
        email.content_subtype = "html"

        # Handle file paths for attachments
        for attachment in attachments:
            if isinstance(attachment, str) and os.path.exists(attachment):
                email.attach_file(attachment)

        email.send(fail_silently=False)

@shared_task(bind=True, max_retries=3)
def notify(self, to, subject, body, cc=None, attachments=[]):
    footer = build_footer()
    body += footer
    prefix = build_subj_prefix()
    subject = prefix + subject
    if not settings.DUMMY_EMAILS:
        try:
            g = gmailapi()
            g.send(to, subject, body, attachments=attachments, cc=cc)
        except Exception as error:
            print(f'An error occurred while sending email: {error}')
            raise self.retry(exc=error, countdown=10)
    else:
        print('From: %s' % settings.DEFAULT_FROM_EMAIL)
        print('To: %s' % to)
        print('cc: %s' % cc)
        print('Subject: %s' % subject)
        print('Message: %s' % body)
