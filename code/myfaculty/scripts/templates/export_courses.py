from curricula.models import Course, StudyProgram
import csv

program_code = 1

def run():    
    with open('courses.csv','w') as f:
        writer = csv.writer(f, delimiter=';', quoting = csv.QUOTE_ALL)        
        objs = Course.objects.filter(program__pk=program_code).order_by('semester').all()
        i = 0
        for obj in objs:
            d = {
                "id": obj.id,
                "program": obj.program.title_gr,
                "code_gr": obj.code_gr,
                "code_en": obj.code_en,
                "semester": obj.semester,
                "title_gr": obj.title_gr,
                "title_en": obj.title_en,
                "weekly_hours": obj.weekly_hours,
                "weekly_lab_hours": obj.weekly_lab_hours,
                "ects_credits": obj.ects_credits,
                "type_gr": obj.type_gr,
                "type_en": obj.type_en,
                "prequesites_gr": obj.prequesites_gr,
                "prequesites_en": obj.prequesites_en,
                "url": obj.url,
                "language_gr": obj.language_gr,
                "language_en": obj.language_en,
                "offered_erasmus": obj.offered_erasmus,
                "outcomes_gr": obj.outcomes_gr,
                "outcomes_en": obj.outcomes_en,
                "skills_gr": obj.skills_gr,
                "skills_en": obj.skills_en,
                "content_gr": obj.content_gr,
                "content_en": obj.content_en,
                "delivery_gr": obj.delivery_gr,
                "delivery_en": obj.delivery_en,
                "evaluation_gr": obj.evaluation_gr,
                "evaluation_en": obj.evaluation_en,
                "ict_gr": obj.ict_gr,
                "ict_en": obj.ict_en,
                "bibliography_gr": obj.bibliography_gr,
                "bibliography_en": obj.bibliography_en,
                "journals": obj.journals,
                "active": obj.active,
                "required_math": obj.required_math,
                "required_lab": obj.required_lab,
                "display_name": obj.display_name,
                "elective": obj.elective,
                "hours_lecturing": obj.hours_lecturing,
                "hours_lab": obj.hours_lab,
                "hours_study": obj.hours_study,
                "hours_project": obj.hours_project,
                "hours_lab_prep": obj.hours_lab_prep,
                "hours_total": obj.hours_total,
                "required_math" : obj.required_math,
                "required_lab" : obj.required_lab
            }
            if i==0:
                writer.writerow(d.keys())
            l = [d[k] for k in d.keys()]
            i += 1
            writer.writerow(l)
