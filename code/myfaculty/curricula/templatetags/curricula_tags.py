from django import template
from curricula.models import Course
from django.urls import reverse
from django.utils.html import mark_safe

register = template.Library()

@register.filter(name="as_course_table")
def as_course_table(courses):
    obl_course_list = [{'code' : c.code_gr,
                    'title' : c.title_gr,
                    'semester' : int(c.semester),
                    'link' : reverse('curricula:public_detail_course',args=[c.pk])} 
                    for c in courses if c.active and not c.elective 
                    ].sort(key = lambda x: (x['semester'], x['code']))
    elec_course_list = [{'code' : c.code_gr,
                    'title' : c.title_gr,
                    'semester' : int(c.semester),
                    'link' : reverse('curricula:public_detail_course',args=[c.pk])} 
                    for c in courses if c.active and c.elective 
                    ].sort(key = lambda x: (x['semester'], x['code']))
    
    result = ""

    semester_max = max([int(c.semester) for c in courses])

    for s in range(semester_max):
        #obj_sem = [c for c in obl_course_list if c['semester'] == s+1 ]
        #elec_sem = [c for c in elec_course_list if c['semester'] == s+1 ]
        result = result + """
        <h4> Εξάμηνο {s} </h4>
        """
        obj_sem = [c for c in obl_course_list if c['semester'] == s+1 ]
        if len(obj_sem) > 0:
            result += """
            <table class="table">
            <thead>
            <tr>
                <th scope="col">Κωδικός</th>
                <th scope="col">Τίτλος</th>       
                <th></th>      
            </tr>
            </thead>
            </table>    
            """.format(s = s+1)
    
    return mark_safe(result)

@register.filter(name="get_element")
def get_element(c, i):
    if i in c:
        return c[i]