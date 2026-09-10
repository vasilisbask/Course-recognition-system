from theses.models import Thesis
from scopes.models import Secretariat
from myprofile.models import create_user_if_required
from curricula.models import StudyProgram, Department
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
DEP_TITLE = 'Πληροφορικής και Τηλεματικής'
TITLE_GR = 'Διδακτορικό Πρόγραμμα Σπουδών'
TITLE_EN = 'PhD Programme'

secs_progs = {
    'itsec' : ['Προπτυχιακό Πρόγραμμα Σπουδών', 'Προπτυχιακό Πρόγραμμα Σπουδών (Παλιό)'],
    'applied' : ['ΠΜΣ Εφαρμοσμένη Πληροφορική'],
    'itpsec' : ['ΠΜΣ Πληροφορική και Τηλεματική', 'Προηγμένες Τεχνολογίες Πληροφορικής και Εφαρμογές'],
    'mphilsec' : ['ΠΜΣ Επιστήμη των Υπολογιστών και Πληροφορική'],
    'itphdsec' : [ TITLE_GR ]
}

dep_secs = ['apresvelou']

def run():
    # Create doctoral program

    secretariats = Secretariat.objects.all()
    for secretariat in secretariats:
        secretariat.delete()
    
    department = Department.objects.filter(title_gr = DEP_TITLE).first()

    doctoral_programs = StudyProgram.objects.filter(title_gr = TITLE_GR, department = department)
    if not doctoral_programs.exists():

        doctoral_program = StudyProgram(
            title_gr = TITLE_GR,
            title_en = TITLE_EN,
            department = department
        )    
        doctoral_program.save()    
    
    for sec_user, secs_prog in secs_progs.items():
        email = sec_user + '@' + settings.INTERNAL_DOMAIN
        user = create_user_if_required(email)
        if not user:
            user = User.objects.get(email=email)
        programs = StudyProgram.objects.filter(title_gr__in = secs_prog)
        secretariat = Secretariat(
            user = user,
        )
        secretariat.save()
        secretariat.programs.set(programs)
        secretariat.save()

    for sec_user in dep_secs:
        email = sec_user + '@' + settings.INTERNAL_DOMAIN
        user = create_user_if_required(email)
        if not user:
            user = User.objects.get(email=email)
        secretariat = Secretariat(
            user = user,
        )
        secretariat.save()       
        secretariat.departments.set([department])
        secretariat.save()

        

    

    




