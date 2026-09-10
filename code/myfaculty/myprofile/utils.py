from django.http import Http404
from mailer.gmail import notify
from django.conf import settings
from django.core.signing import TimestampSigner
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.conf import settings
def get_domain_uri(request):
    domain = request.build_absolute_uri('/')[:-1]
    if 'http://' in domain:
        domain = domain.replace('http://', 'https://')
    return domain


def send_password_link(request, email):
    domain = get_domain_uri(request)
    invitation = {
        'email' : email                    
    }
    signer = TimestampSigner()
    signed_data = signer.sign_object(invitation)
    url = domain + reverse_lazy('myprofile:password_token', kwargs={'token' : signed_data})
    body = settings.FORGOT_PASSWORD_BODY.format(url=url)
    notify.delay(email, settings.FORGOT_PASSWORD_SUBJECT, body)

def complexity_message():
    msg1 = _("Για το κωδικό σας πρέπει να χρησιμοποιήσετε κωδικό που να περιέχει τουλάχιστον %(num)d χαρακτήρες με:") % {
        'num': settings.MIN_LENGTH
    }
    msg2 = _("%(num)d τουλάχιστον λατινικούς κεφαλαίους χαρακτήρες") % {'num': settings.UPPERCASE_MIN}
    msg3 = _("%(num)d τουλάχιστον λατινικούς μικρούς χαρακτήρες") % {'num': settings.LOWERCASE_MIN}
    msg4 = _("%(num)d τουλάχιστον ψηφία (0 εώς 9)") % {'num': settings.DIGITS_MIN}
    msg5 = _("%(chars)d τουλάχιστον ειδικούς χαρακτήρες από %(special)s") % {
        'chars': settings.SPECIAL_CHARACTERS_MIN,
        'special': settings.PASSWORD_SPECIAL_CHARS
    }
    msg6 = _("Μην χρησιμοποιείτε άλλους χαρακτήρες εκτός ψηφίων, των ειδικών χαρακτήρων και λατινικών χαρακτήρων")

    return """
        %s
        <ul>
            <li> %s </li>
            <li> %s </li>
            <li> %s </li>
            <li> %s </li>
            <li> %s </li>                                          
        </ul>                    
    """ % (msg1, msg2, msg3, msg4, msg5, msg6)