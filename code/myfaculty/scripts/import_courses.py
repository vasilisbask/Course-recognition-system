from scripts.budi import budiapi
from curricula.models import School, Department, StudyProgram, Course
from myprofile.models import StaffMember
from django.forms.models import model_to_dict
def run():
    b = budiapi()


    courses = b.get_table_data('courses','ects')
    # schoolsGr = list(set([c['schoolGr'] for c in courses]))
    # schoolsEn = list(set([c['schoolEn'] for c in courses]))
    # DepartmentGr = list(set([c['departmentGr'] for c in courses]))
    # DepartmentEn = list(set([c['departmentEn'] for c in courses]))
    # DepartmentGr = list(set([c['departmentGr'] for c in courses]))
    # DepartmentEn = list(set([c['departmentEn'] for c in courses]))
    # academicProgrammes2 = list(set( [(c['academicProgrammeGr'],c['academicProgrammeEn']) for c in courses]))
    # academicProgrammesEn = []
    # academicProgrammesGr = []
    
    # for program in academicProgrammes2:
    #     gr = program[0]
    #     en = program[1]
    #     if gr not in academicProgrammesGr:
    #         academicProgrammesGr.append(gr)
    #         academicProgrammesEn.append(en)
            
        


    # print(schoolsGr)
    # print(schoolsEn)
    # print(DepartmentGr)
    # print(DepartmentEn)
    # print(academicProgrammesGr)
    # print(academicProgrammesEn)

    # school = School(title_gr = schoolsGr[0], 
    #                 title_en = schoolsEn[0])
    # school.save()
    # department = Department(title_gr = DepartmentGr[0],
    #                         title_en = DepartmentEn[0], 
    #                         school = school)
    # department.save()

    # for i, p in enumerate(academicProgrammesGr):
    #     study_program = StudyProgram(
    #         title_gr = p,
    #         title_en = academicProgrammesEn[i],
    #         department = department
    #     )
    #     study_program.save()

    for c in courses:
        program = StudyProgram.objects.get(title_gr = c['academicProgrammeGr'])

        co = Course(
            program = program,
            code_gr = c.get('codeGr',''),
            code_en = c.get('codeEn',''),
            semester = c.get('semester',''),
            title_gr = c.get('titleGr',''),
            title_en = c.get('titleEn',''),
            weekly_hours = c.get('hoursPerWeek',''),
            weekly_lab_hours = 0,
            ects_credits = c.get('ectsCredits',''),
            type_gr = c.get('courseTypeGr',''),
            type_en = c.get('courseTypeEn',''),
            prequesites_gr = c.get('prequisiteCoursesGr',''),
            prequesites_en = c.get('prequisiteCoursesEn',''),
            url = c.get('url',''),
            language_gr = c.get('courseLanguageGr',''),
            language_en = c.get('courseLanguageEn',''),   
            offered_erasmus = True,
            outcomes_gr = c.get('outcomesGr',''),
            outcomes_en = c.get('outcomesEn',''),
            skills_gr = c.get('skillsObtainedGr',''),
            skills_en = c.get('skillsObtainedEn',''),
            content_gr = c.get('courseContentGr',''),
            content_en = c.get('courseContentEn',''),
            delivery_gr = 'Δια ζώσης',
            delivery_en = 'Face-to-face',
            ict_gr = c.get('usageofICTGr',''),
            ict_en = c.get('usageOfICTEn',''),
            bibliography_gr = c.get('bibliographyGr',''),
            bibliography_en = c.get('bibliographyEn',''),
            journals = c.get('journals',''),
            active = c.get('active',False),
            evaluation_gr = c.get('evaluationMeansGr',''),
            evaluation_en = c.get('EvaluationMeansEn',''),            
            hours_lecturing = c.get('hoursLecturing',0),
            hours_lab = c.get('hoursLab',0),
            hours_project = c.get('hoursProject',0),
            hours_lab_prep = c.get('hoursLabReport',0),
            hours_total = c.get('totalHours',0),
            hours_study = c.get('hoursStudy',0),
            elective = not c.get('isCompulsory',True),
          )
        co.save()
        assigned_to = [ c['assignedToEmail'] ]
        for i in range(2, 6):        
            key = 'assigned' + str(i)
            if key in c:
                assigned_to.append(c[key])
        
        staff = []
        for email in assigned_to:
            s = StaffMember.objects.filter(email = email)
            if len(s) == 1:
                staff.append(s[0]) 
        
        co.assigned_to.set(staff)
        co.save()
        print('Created %s' %co.title_gr)
