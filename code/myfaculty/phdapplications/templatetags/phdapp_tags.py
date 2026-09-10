from django import template
from django.utils.safestring import mark_safe
from phdapplications.models import Degree, WorkExperience, ConferencePublication, JournalPublication, ReferenceContact, ReferenceLetter, Call, Application
from django.urls import reverse_lazy
#from phdapplications.utils import get_object_short
from django.utils.translation import gettext_lazy as _

register = template.Library()

# def table_cells(obj):
#      if isinstance(obj, Degree):
#         html = f"""
#             <td>
#             {obj.year}
#             </td>
#             <td>
#             {obj.school}
#             </td>
#             <td>
#             {obj.university}
#             </td>
#             <td>
#             {obj.type}
#             </td>    
                          
#         """
#      elif isinstance(obj, WorkExperience):
#         html = f"""
#                 <td>
#                 {obj.start_date.year}
#                 </td>
#                 <td>
#                 {obj.company}
#                 </td>
#                 <td>
#                 {obj.title}
#                 </td>                              
#         """ 
#      elif isinstance(obj, ConferencePublication):
#         html = f"""
#             <td>
#             {obj.year}
#             </td>
#             <td>
#             {obj.title}
#             </td>
#             <td>
#             {obj.conference_title}
#             </td>                              
#         """
#      elif isinstance(obj, JournalPublication):
#         html = f"""
#             <td>
#             {obj.year}
#             </td>
#             <td>
#             {obj.title}
#             </td>
#             <td>
#             {obj.journal_title}
#             </td>
#             <td>
#             {obj.publisher}
#             </td>             
#         """
#      elif isinstance(obj, ReferenceContact):
#         html = f"""
#             <td>
#             {obj.contact_given_name}
#             </td>
#             <td>
#             {obj.contact_surname}
#             </td>
#             <td>
#             {obj.contact_institution}
#             </td>            
#         """
#      elif isinstance(obj, ReferenceLetter):
#         html = f"""
#             <td>
#             {obj.contact_given_name}
#             </td>
#             <td>
#             {obj.contact_surname}
#             </td>
#             <td>
#             {obj.contact_institution}
#             </td>       
#             <td>
#             {obj.submitted_date}
#             </td>                        
#         """
#      elif isinstance(obj, Call):
#          html = f"""
#             <td>
#             {obj.start}
#             </td>
#             <td>
#             {obj.end}
#             </td>
#             <td>
#             {obj.title}
#             </td>
#             <td>
#             {obj.supervisor.display_name}
#             </td>            
#          """
     
#      return mark_safe(html)

# def make_row(html, edit_url="", include_button=True, button_text=_('Επεξεργασία')):
#     html= """
#            <tr>
#            """ + html + """

#            """ 
#     if include_button:
#         html += f"""<td>
#                 <a href="{edit_url}" type="submit" class="btn btn-primary tablebutton">{button_text}</a>     
#             </td>              
#             </tr>
#           """ 
#     return mark_safe(html)

# @register.filter(name='as_sec_call_row')
# def as_sec_call_row(obj):
#    edit_url = reverse_lazy('phdapplications:sec_call_edit', kwargs = {'pk' :obj.id})
#    application_url = reverse_lazy('phdapplications:sec_call_applicant_list', kwargs = {'pk' :obj.id})
   
#    button_html = f"""
#    <td>
#       <a href="{edit_url}" type="submit" class="btn btn-primary tablebutton"> Επεξεργασία </a>  
#       <a href="{application_url}" type="submit" class="btn btn-success tablebutton"> Αιτήσεις </a>      
#    </td>           
#    """ 
   
#    cell_html = table_cells(obj)
#    html = """
#     <tr>
#    """ + cell_html + button_html + """
#    </tr>
#    """
#    return mark_safe(html)

# @register.filter(name='as_reviewer_call_row')
# def as_reviewer_call_row(obj):
#    application_url = reverse_lazy('phdapplications:reviewer_call', kwargs = {'pk' :obj.id})
#    button_text= _('Αιτήσεις')

#    button_html = f"""
#    <td>
#       <a href="{application_url}" type="submit" class="btn btn-success tablebutton">{button_text}  </a>      
#    </td>           
#    """ 
   
#    cell_html = table_cells(obj)
#    html = """
#     <tr>
#    """ + cell_html + button_html + """
#    </tr>
#    """
#    return mark_safe(html)

# @register.filter(name='as_reviewer_application_table_headers')
# def as_reviewer_application_table_headers(objs):
#     name = _('Όνομα')
#     surname = _('Επώνυμο')
#     submission = _('Υποβολή')
#     html = f"""
#     <thead>
#       <tr>
#         <th scope="col">{name}</th>        
#         <th scope="col">{surname}</th>
#         <th scope="col">{submission}</th>
#          <th></th>
#       </tr>
#     </thead>    
#     """
#     return mark_safe(html)


# @register.filter(name='as_reviewer_application_row')
# def as_reviewer_application_row(obj):
#     application_url = reverse_lazy('phdapplications:application_summary', kwargs={'role' : 'reviewer', 'pk' : obj.pk})
#     button_text = _('Λεπτομέρειες')
#     html = f"""
#         <tr>
#         <td>
#         {obj.applicant.name}
#         </td>
#         <td>
#         {obj.applicant.surname}
#         </td>
#         <td>
#         {obj.date_submitted}
#         </td>
#         <td>
#             <a href="{application_url}" type="submit" class="btn btn-success tablebutton"> {button_text} </a>      
#         </td>        
#         </tr>
#     """
#     return mark_safe(html)

# def html_headers(*header_titles):
#     html = """
#         <thead>
#         <tr>
#     """
#     for title in header_titles:
#         html += """
#         <th scope="col">%s</th>
#         """ % title
#     html += """                    
#         <th></th>    
#         </tr>
#         </thead>
#     """
#     return html

# @register.filter(name='table_headers')
# def table_headers(objs):
#     if isinstance(objs, list):
#         count = len(objs)
#     else:
#         count = objs.count()

#     year = _('Έτος')
#     school = _('Σχολή')
#     institution = _('Ίδρυμα')
#     typ = _('Τύπος')
#     start_date = _('Έναρξη')
#     organization = _('Φορέας')
#     title = _('Τίτλος')
#     conf = _('Συνέδριο')
#     journal = _('Περιοδικό')
#     house = _('Εκδοτικός Οίκος')
#     submission_date = _('Ημερομηνία υποβολής')
#     end_date = _('Λήξη')
#     supervisor = _('Επιβλέπων')
#     name = _('Όνομα')
#     surname = _('Επώνυμο')
        
#     if count > 0:
#         if isinstance(objs[0], Degree):
#             html = html_headers(year, school, institution, typ)
#         elif isinstance(objs[0], WorkExperience):
#             html = html_headers(start_date, institution, title)
#         elif isinstance(objs[0], ConferencePublication):
#             html = html_headers(year, title, conf)
#         elif isinstance(objs[0], JournalPublication):
#             html = html_headers(year, title, journal, house)
#         elif isinstance(objs[0], ReferenceContact):
#             html = html_headers(name, surname, organization)
#         elif isinstance(objs[0], ReferenceLetter):
#             html = html_headers(name, surname, organization, submission_date)
#         elif isinstance(objs[0], Call):
#             html = html_headers(start_date, end_date, title, supervisor)        
#     return mark_safe(html)

# @register.filter(name='as_sec_table_row')
# def as_sec_table_row(obj):
#     obj_id = obj.pk
#     obj_type = get_object_short(obj)
#     if isinstance(obj, ReferenceLetter):
#         application_id = obj.doctorate_application.id
#         edit_url = reverse_lazy('phdapplications:sec_obj_application_details', 
#                                  kwargs={'application_id' : application_id,
#                                          'obj_id' : obj_id,
#                                         'obj_type' : obj_type})    
#     else:
#         applicant_id = obj.applicant.pk
#         edit_url = reverse_lazy('phdapplications:sec_detail', 
#                                         kwargs={'applicant_id' : applicant_id,
#                                                 'obj_id' : obj_id,
#                                                 'obj_type' : obj_type})
    
#     html = table_cells(obj)
#     return make_row(html, edit_url=edit_url)

# @register.filter(name='as_reviewer_table_row')
# def as_reviewer_table_row(obj,app_id):
#     obj_id = obj.pk
#     obj_type = get_object_short(obj)
#     edit_url = reverse_lazy('phdapplications:reviewer_obj_details', 
#                              kwargs={'application_id' : app_id,
#                                      'obj_id' : obj_id,
#                                      'obj_type' : obj_type})
#     html = table_cells(obj)
#     return make_row(html, edit_url=edit_url, button_text='Λεπτομέρειες')


# @register.filter(name='as_applicant_table_row')
# def as_applicant_table_row(obj):
#     obj_id = obj.pk
#     obj_type = get_object_short(obj)
#     if not isinstance(obj, ReferenceLetter):
#        edit_url = reverse_lazy('phdapplications:applicant_obj_detail', 
#                                 kwargs={'obj_id' : obj_id, 
#                                         'obj_type' : obj_type})
#        include_button = True
#     else:
#         edit_url=None
#         include_button = False
       
#     html = table_cells(obj)
#     return make_row(html, edit_url=edit_url, include_button=include_button)


# @register.filter(name='as_reference_application_table_row')
# def as_reference_application_table_row(obj):
#     html = f"""
#           <td>
#           {obj.contact_given_name}
#           </td>
#           <td>
#           {obj.contact_surname}
#           </td>
#           <td>
#           {obj.contact_institution}
#           </td>            
#     """   
#     return make_row(html, edit_url=None, include_button=False)


# @register.filter(name='as_call_table')
# def as_call_table(objs, id):
#     if objs.count() == 0:
#         message = _('Δεν υπάρχουν καταχωρήσεις σε αυτή την κατηγορία')
#         html = _("""
#         <p> %s </p>
#         """) % message
#     else:
#         html = f"""
#             <script>
#             $(document).ready(function() {{
#             $('#{id}').DataTable({{
#                 "lengthChange": false,
#                 "pageLength": 20,
#                 "order" : [[ 0, "desc" ]],
#             }}
#             );
#             }});
#         </script>

#             <table class="table" id="{id}">
#             """ + table_headers(objs) + """
#             <tbody>
#             """
        
#         for obj in objs:
#             html += as_sec_call_row(obj)
        
#         html += """
#             </tbody>
#             </table>
#             """
        
#     return mark_safe(html)
            


