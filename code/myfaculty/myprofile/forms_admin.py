from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.models import Case, IntegerField, Value, When
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from curricula.models import Department, StudyProgram
from scopes.models import Secretariat
from .checks import validate_password
from .models import Student


User = get_user_model()
REQUIRED_ERROR_MESSAGES = {"required": _("Συμπληρώστε αυτό το πεδίο.")}


def admin_password_help_text(is_edit=False):
    prefix = ""
    if is_edit:
        prefix = f"<p class=\"mb-1\">{_('Αφήστε το κενό αν δεν θέλετε αλλαγή συνθηματικού.')}</p>"
    return mark_safe(
        prefix
        + """
        <p class="mb-1">{intro}</p>
        <ul class="mt-0 mb-1">
          <li>{uppercase}</li>
          <li>{lowercase}</li>
          <li>{digit}</li>
          <li>{special}</li>
        </ul>
        <p class="mb-0">{allowed}</p>
        """.format(
            intro=_("Ο κωδικός πρέπει να περιέχει τουλάχιστον 8 χαρακτήρες και:"),
            uppercase=_("1 λατινικό κεφαλαίο γράμμα"),
            lowercase=_("1 λατινικό πεζό γράμμα"),
            digit=_("1 αριθμό από 0 έως 9"),
            special=_("2 ειδικούς χαρακτήρες από {}!@#$%^&*()-+"),
            allowed=_("Επιτρέπονται μόνο λατινικά γράμματα, αριθμοί και οι παραπάνω ειδικοί χαρακτήρες."),
        )
    )


class BootstrapFormMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                continue
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class StudyProgramChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.type == StudyProgram.UNDERGRADUATE:
            return _("Προπτυχιακό Πρόγραμμα Σπουδών")
        if obj.type == StudyProgram.POSTGRADUATE:
            return _("Μεταπτυχιακό Πρόγραμμα Σπουδών")
        return str(obj)


def study_program_queryset():
    # Show undergraduate programs before postgraduate ones in admin forms.
    return StudyProgram.objects.filter(
        active=True,
        type__in=[StudyProgram.UNDERGRADUATE, StudyProgram.POSTGRADUATE],
    ).annotate(
        type_order=Case(
            When(type=StudyProgram.UNDERGRADUATE, then=Value(0)),
            When(type=StudyProgram.POSTGRADUATE, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by("type_order", "title_gr")


class AdminSecretariatUserForm(BootstrapFormMixin, forms.Form):
    given_name = forms.CharField(label=_("Όνομα"), max_length=150, error_messages=REQUIRED_ERROR_MESSAGES)
    surname = forms.CharField(label=_("Επώνυμο"), max_length=150, error_messages=REQUIRED_ERROR_MESSAGES)
    username = forms.CharField(label=_("Username"), max_length=150, error_messages=REQUIRED_ERROR_MESSAGES)
    email = forms.EmailField(label=_("Email"), error_messages=REQUIRED_ERROR_MESSAGES)
    password = forms.CharField(
        label=_("Συνθηματικό"),
        widget=forms.PasswordInput,
        required=True,
        error_messages=REQUIRED_ERROR_MESSAGES,
    )
    password_confirm = forms.CharField(
        label=_("Επιβεβαίωση συνθηματικού"),
        widget=forms.PasswordInput,
        required=True,
        error_messages=REQUIRED_ERROR_MESSAGES,
    )
    program = StudyProgramChoiceField(
        label=_("Πρόγραμμα Σπουδών"),
        queryset=StudyProgram.objects.none(),
        empty_label=None,
        error_messages=REQUIRED_ERROR_MESSAGES,
    )
    departments = forms.ModelMultipleChoiceField(
        label=_("Τμήματα"),
        queryset=Department.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        error_messages=REQUIRED_ERROR_MESSAGES,
    )

    def __init__(self, *args, user=None, secretariat=None, **kwargs):
        self.user = user
        self.secretariat = secretariat
        super().__init__(*args, **kwargs)
        self.fields["program"].queryset = study_program_queryset()
        self.fields["departments"].queryset = Department.objects.all().order_by("title_gr")
        self.fields["password"].help_text = admin_password_help_text(is_edit=bool(self.user))

        if self.user:
            self.fields["password"].required = False
            self.fields["password_confirm"].required = False
            self.fields["password_confirm"].help_text = _("Αφήστε το κενό αν δεν θέλετε αλλαγή συνθηματικού.")
            self.initial.setdefault("given_name", self.user.first_name)
            self.initial.setdefault("surname", self.user.last_name)
            self.initial.setdefault("username", self.user.username)
            self.initial.setdefault("email", self.user.email)
        if self.secretariat:
            self.initial.setdefault("program", self.secretariat.programs.first())
            self.initial.setdefault("departments", self.secretariat.departments.all())

        self.apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        # On edit, an empty password means that the existing password is kept.
        if not self.user and not password:
            self.add_error("password", _("Το συνθηματικό είναι υποχρεωτικό."))
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(_("Τα συνθηματικά δεν ταιριάζουν."))
            try:
                validate_password(password, password_confirm)
            except forms.ValidationError as error:
                self.add_error("password", error)
        if username and User.objects.filter(username=username).exclude(pk=getattr(self.user, "pk", None)).exists():
            self.add_error("username", _("Υπάρχει ήδη χρήστης με αυτό το username."))
        if email and User.objects.filter(email=email).exclude(pk=getattr(self.user, "pk", None)).exists():
            self.add_error("email", _("Υπάρχει ήδη χρήστης με αυτό το email."))

        return cleaned_data

    def save(self):
        user = self.user or User(username=self.cleaned_data["username"])
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["given_name"]
        user.last_name = self.cleaned_data["surname"]
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        user.save()
        user.groups.clear()
        user.user_permissions.clear()

        secretariat = self.secretariat or Secretariat.objects.filter(user=user).first() or Secretariat(user=user)
        secretariat.user = user
        secretariat.save()
        secretariat.programs.set([self.cleaned_data["program"]])
        secretariat.departments.set(self.cleaned_data["departments"])
        return user


class AdminStudentUserForm(BootstrapFormMixin, forms.Form):
    given_name = forms.CharField(label=_("Όνομα"), max_length=50, error_messages=REQUIRED_ERROR_MESSAGES)
    surname = forms.CharField(label=_("Επώνυμο"), max_length=70, error_messages=REQUIRED_ERROR_MESSAGES)
    email = forms.EmailField(label=_("Email"), error_messages=REQUIRED_ERROR_MESSAGES)
    password = forms.CharField(
        label=_("Συνθηματικό"),
        widget=forms.PasswordInput,
        required=True,
        error_messages=REQUIRED_ERROR_MESSAGES,
    )
    password_confirm = forms.CharField(
        label=_("Επιβεβαίωση συνθηματικού"),
        widget=forms.PasswordInput,
        required=True,
        error_messages=REQUIRED_ERROR_MESSAGES,
    )
    reg_num = forms.CharField(
        label=_("Αριθμός μητρώου"),
        max_length=70,
        error_messages=REQUIRED_ERROR_MESSAGES,
        validators=[
            RegexValidator(
                regex=r"^\d+$",
                message=_("Ο αριθμός μητρώου πρέπει να περιέχει μόνο αριθμούς."),
            )
        ],
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "title": _("Ο αριθμός μητρώου πρέπει να περιέχει μόνο αριθμούς."),
                "oninput": "this.value = this.value.replace(/\\D/g, '');",
            }
        ),
    )
    program = StudyProgramChoiceField(
        label=_("Πρόγραμμα Σπουδών"),
        queryset=StudyProgram.objects.none(),
        empty_label=None,
        error_messages=REQUIRED_ERROR_MESSAGES,
    )
    semester = forms.IntegerField(
        label=_("Εξάμηνο"),
        min_value=1,
        max_value=8,
        error_messages={
            "required": _("Συμπληρώστε αυτό το πεδίο."),
            "min_value": _("Η τιμή πρέπει να είναι από 1 έως 8."),
            "max_value": _("Η τιμή πρέπει να είναι από 1 έως 8."),
        },
    )

    def __init__(self, *args, student=None, **kwargs):
        self.student = student
        self.user = student.user if student and student.user_id else None
        super().__init__(*args, **kwargs)
        self.fields["program"].queryset = study_program_queryset()
        self.fields["password"].help_text = admin_password_help_text(is_edit=bool(self.student))
        self.fields["semester"].widget.attrs.update(
            {
                "min": 1,
                "max": 8,
                "data-range-message": _("Η τιμή πρέπει να είναι από 1 έως 8."),
            }
        )

        if self.student:
            self.fields["password"].required = False
            self.fields["password_confirm"].required = False
            self.fields["password_confirm"].help_text = _("Αφήστε το κενό αν δεν θέλετε αλλαγή συνθηματικού.")
            self.initial.setdefault("given_name", self.student.given_name)
            self.initial.setdefault("surname", self.student.surname)
            self.initial.setdefault("email", self.student.email or (self.user.email if self.user else ""))
            self.initial.setdefault("reg_num", self.student.reg_num)
            self.initial.setdefault("program", self.student.program)
            self.initial.setdefault("semester", self.student.semester)

        self.apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if not self.student and not password:
            self.add_error("password", _("Το συνθηματικό είναι υποχρεωτικό."))
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(_("Τα συνθηματικά δεν ταιριάζουν."))
            try:
                validate_password(password, password_confirm)
            except forms.ValidationError as error:
                self.add_error("password", error)
        if email:
            # Student usernames are derived from the institutional email prefix.
            cleaned_data["username"] = email.split("@", 1)[0]
            if User.objects.filter(username=cleaned_data["username"]).exclude(pk=getattr(self.user, "pk", None)).exists():
                self.add_error("email", _("Υπάρχει ήδη χρήστης με αυτό το email/username."))
            if User.objects.filter(email=email).exclude(pk=getattr(self.user, "pk", None)).exists():
                self.add_error("email", _("Υπάρχει ήδη χρήστης με αυτό το email."))

        return cleaned_data

    def save(self):
        user = self.user or User(username=self.cleaned_data["username"])
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["given_name"]
        user.last_name = self.cleaned_data["surname"]
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        user.save()
        user.groups.clear()
        user.user_permissions.clear()

        student = self.student or Student(user=user)
        student.user = user
        student.username = user.username
        student.email = user.email
        student.given_name = self.cleaned_data["given_name"]
        student.surname = self.cleaned_data["surname"]
        student.reg_num = self.cleaned_data["reg_num"]
        student.semester = self.cleaned_data["semester"]
        student.program = self.cleaned_data["program"]
        student.save()
        return user
