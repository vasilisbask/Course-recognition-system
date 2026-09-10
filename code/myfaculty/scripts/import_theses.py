from myprofile.models import StaffMember, Student
from theses.models import Thesis
from curricula.models import StudyProgram
import csv

def run():
    FILENAME = 'scripts/ptyxiakes1.csv.tpl'
    USERNAME_PREFIX = 'it'
    OFFERED_IN = 'ΠΠΣ'

    with open(FILENAME, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for d in reader:
            username = USERNAME_PREFIX + d['Αριθμός Μητρώου']
            title_gr = d['Τίτλος Πτυχιακής Εργασίας'].split('(')[0].strip()
            title_en = d['Τίτλος Πτυχιακής Εργασίας στα Αγγλικά'].strip()
            abstract = title_gr
            s = d['supervisor'] + '@hua.gr'
            m1 = d['member1'] +'@hua.gr'
            m2 = d['member2'] +'@hua.gr'
            

            supervisor = StaffMember.objects.get(email = s)
            member1 = StaffMember.objects.get(email = m1)
            member2 = StaffMember.objects.get(email = m2)
            assigned_to = Student.objects.get_profile(username)
            offered_in = StudyProgram.objects.get(short_gr=OFFERED_IN)
            e = Thesis.objects.filter(assigned_to = assigned_to)
            if e.count() == 0:
                t = Thesis(
                    title_gr = title_gr,
                    title_en = title_en,
                    abstract = abstract,
                    supervisor = supervisor,
                    member1 = member1,
                    member2 = member2,
                    assigned_to = assigned_to,
                    is_offered=False
                )
                print('Creating new thesis',title_gr, assigned_to)
                t.save()
                t.offered_in.add(offered_in)
            else: 
                print(title_gr,assigned_to, 'already has a thesis', e[0])


