from django import forms
from .models import Course
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, HTML
from django.core.exceptions import ValidationError
from dal import autocomplete

COURSE_FIELDS = ['program', 
                 'code_gr', 
                 'code_en', 
                 'semester',
                 'active',
                'title_gr',
                'title_en' ,    
                'weekly_hours', 
                'weekly_lab_hours',
                'ects_credits' ,
                'type_gr', 
                'type_en' ,
                'prequesites_gr',
                'prequesites_en' ,   
                'url',
                'language_gr', 
                'language_en', 
                'offered_erasmus',
                'outcomes_gr',
                'outcomes_en',
                'skills_gr' ,
                'skills_en' ,
                'content_gr' ,
                'content_en' ,
                'delivery_gr' ,
                'delivery_en' ,
                'ict_gr' ,
                'ict_en' ,
                'assigned_to',
                'elective', 
                'hours_lecturing', 
                'hours_lab', 
                'hours_study', 
                'hours_project', 
                'hours_lab_prep',
                'required_math',
                'required_lab',
                'bibliography_gr',
                'bibliography_en',
                'evaluation_gr',
                'evaluation_en',                
                 ] 

PUBLIC_COURSE_FIELDS = ['program', 
                        'code_gr', 
                        'semester',
                        'title_gr',
                        'weekly_hours', 
                        'ects_credits' ,
                        'type_gr', 
                        'prequesites_gr',
                        'url',
                        'outcomes_gr',
                        'skills_gr' ,
                        'content_gr' ,
                        'ict_gr' ,                    
                        'elective'
                      ] 


PUBLIC_COURSE_FIELDS_EN = ['code_en', 
                        'semester',
                        'title_en',
                        'weekly_hours', 
                        'ects_credits' ,
                        'type_en', 
                        'prequesites_en',
                        'url',
                        'outcomes_en',
                        'skills_en' ,
                        'content_en' ,
                        'ict_en' ,                    
                        'elective'
                      ] 

PUBLIC_COURSE_FIELDS_H = ['hours_lecturing', 
                          'hours_lab', 
                          'hours_study', 
                          'hours_project', 
                          'hours_lab_prep' ]

COURSE_OBLIGATORY_FIELDS_STAFF = ['prequesites_gr',
                'prequesites_en' ,   
                'url',
                'language_gr', 
                'language_en', 
                'offered_erasmus',
                'outcomes_gr',
                'outcomes_en',
                'skills_gr' ,
                'skills_en' ,
                'content_gr' ,
                'content_en' ,
                'delivery_gr' ,
                'delivery_en' ,
                'ict_gr' ,
                'ict_en' ,
                'assigned_to',
                'hours_study', 
                'hours_project', 
                'hours_lab_prep',
                'bibliography_gr',
                'bibliography_en',
                'evaluation_gr',
                'evaluation_en',                  
                ]

COURSE_DISABLED_FIELDS_STAFF =  ['program', 
                 'code_gr', 
                 'active',
                 'code_en', 
                 'semester',
                'title_gr',
                'title_en' ,    
                'weekly_hours', 'assigned_to', 'ects_credits' ]

COURSE_LABELS = {'program' : 'Πρόγραμμα Σπουδών', 
                 'code_gr' : 'Κωδικός Μαθήματος (Ελληνικά)',
                 'code_en' : 'Κωδικός Μαθήματος (Αγγλικά)',
                 'semester' : 'Εξάμηνο',
                 'active' : 'Ενεργό;',
                'title_gr' : 'Τίτλος (Ελληνικά)',
                'title_en' : 'Τίτλος (Αγγλικά)',
                'weekly_hours' : 'Ώρες Διδασκαλίας Θεωρίας (Εβδομαδιαία)',
                'weekly_lab_hours' : 'Ώρες Διδασκαλίας Εργαστηρίου (Εβδομαδιαία ανά τμήμα)',                
                'ects_credits' : 'Μονάδες ECTS',
                'type_gr' : 'Τύπος Μαθήματος (Ελληνικά)',
                'type_en' : 'Τύπος Μαθήματος (Αγγλικά)',
                'prequesites_gr': 'Προαπαιτούμενα (Ελληνικά)',
                'prequesites_en' : 'Προαπαιτούμενα (Αγγλικά)',
                'url': 'URL Μαθήματος (π.χ. στο e-class)',
                'language_gr': 'Γλώσσα Διδασκαλίας (Ελληνικά)', 
                'language_en': 'Γλώσσα Διδασκαλίας (Αγγλικά)',
                'offered_erasmus': 'Προσφέρεται σε Erasmus',
                'outcomes_gr': 'Μαθησιακά Αποτελέσματα (Ελληνικά)',
                'outcomes_en': 'Μαθησιακά Αποτελέσματα (Αγγλικά)',
                'skills_gr' : 'Γενικές Δεξιότητες (Ελληνικά)',
                'skills_en' : 'Γενικές Δεξιότητες (Αγγλικά)',
                'content_gr' : 'Περιεχόμενο Μαθήματος (Ελληνικά)',
                'content_en' : 'Περιεχόμενο Μαθήματος (Αγγλικά)',
                'delivery_gr' : 'Τρόπος Παράδοσης (Ελληνικά)',
                'delivery_en' : 'Τρόπος Παράδοσης (Αγγλικά)',
                'ict_gr' : 'Χρήση ΤΠΕ (Ελληνικά)',
                'ict_en' : 'Χρήση ΤΠΕ (Αγγλικά)',
                'assigned_to' : 'Ανάθεση',
                'elective' : 'Είναι επιλογής;',
                'hours_lecturing' : 'Διδασκαλίας', 
                'hours_lab' : 'Εργαστήριο',
                'hours_study' :  'Αυτοδύναμη Μελέτη',
                'hours_project' : 'Εργασία (Project)',
                'hours_lab_prep' : 'Εργαστηριακή Αναφορά',
                'required_lab' : 'Απαιτούμενο λογισμικό για το εργαστήριο',
                'required_math' : 'Απαιτούμενες γνώσεις μαθηματικών',
                'bibliography_gr' : 'Βιβλιογραφία (Ελληνικά)',
                'bibliography_en' : 'Βιβλιογραφία (Αγγλικά)',
                'evaluation_gr' : 'Τρόποι Αξιολόγησης (Ελληνικά)',
                'evaluation_en' : 'Τρόποι Αξιολόγησης  (Αγγλικά)',      
                 } 

COURSE_LABELS_EN = {
                'program': 'Study Program',
                'code_gr': 'Course Code (Greek)',
                'code_en': 'Course Code (English)',
                'semester': 'Semester',
                'active': 'Active?',
                'title_gr': 'Title (Greek)',
                'title_en': 'Title (English)',
                'weekly_hours': 'Lecture Hours (Weekly)',
                'weekly_lab_hours': 'Lab Hours (Weekly per Group)',
                'ects_credits': 'ECTS Credits',
                'type_gr': 'Course Type (Greek)',
                'type_en': 'Course Type (English)',
                'prequesites_gr': 'Prerequisites (Greek)',
                'prequesites_en': 'Prerequisites (English)',
                'url': 'Course URL (e.g., on e-class)',
                'language_gr': 'Language of Instruction (Greek)',
                'language_en': 'Language of Instruction (English)',
                'offered_erasmus': 'Offered in Erasmus',
                'outcomes_gr': 'Learning Outcomes (Greek)',
                'outcomes_en': 'Learning Outcomes (English)',
                'skills_gr': 'General Competencies (Greek)',
                'skills_en': 'General Competencies (English)',
                'content_gr': 'Course Content (Greek)',
                'content_en': 'Course Content (English)',
                'delivery_gr': 'Mode of Delivery (Greek)',
                'delivery_en': 'Mode of Delivery (English)',
                'ict_gr': 'Use of ICT (Greek)',
                'ict_en': 'Use of ICT (English)',
                'assigned_to': 'Assigned to',
                'elective': 'Is it elective?',
                'hours_lecturing': 'Lecture Hours',
                'hours_lab': 'Lab Hours',
                'hours_study': 'Independent Study',
                'hours_project': 'Project Work',
                'hours_lab_prep': 'Lab Report',
                'required_lab': 'Required Software for the Lab',
                'required_math': 'Required Mathematical Knowledge',
                
}


COURSE_LAYOUT = Layout(
                    Row(
                        Div(HTML('<h4> Στοιχεία Μαθήματος </h4>'),css_class = 'col-lg-8'),
                        Div(Submit('submit', 'Ενημέρωση'),css_class='col-lg-4 text-end'),
                        css_class="row"),
                    Row(
                        Div(Field('title_gr'),css_class = 'col-lg-6'),
                        Div(Field('title_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                         Div(Field('program'),css_class = 'col-lg-6'),
                         Div(Field('active'),css_class = 'col-lg-6'),
                         css_class="row"),
                    Row(
                        Div(Field('code_gr'),css_class = 'col-lg-4'),
                        Div(Field('code_en'),css_class = 'col-lg-4'),                       
                        Div(Field('semester'),css_class = 'col-lg-4'),
                        css_class="row"),
                    Row(
                        Div(Field('offered_erasmus'),css_class = 'col-lg-4'),
                        Div(Field('elective'),css_class = 'col-lg-4'),
                        Div(Field('ects_credits'),css_class = 'col-lg-4'),
                        css_class="row"),
                    Row(
                        Div(Field('type_gr'),css_class = 'col-lg-6'),
                        Div(Field('type_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('assigned_to'),css_class = 'col-lg-6'),
                        Div(Field('url'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('prequesites_gr'),css_class = 'col-lg-6'),
                        Div(Field('prequesites_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('language_gr'),css_class = 'col-lg-6'),
                        Div(Field('language_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('skills_gr'),css_class = 'col-lg-6'),
                        Div(Field('skills_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('outcomes_gr'),css_class = 'col-lg-6'),
                        Div(Field('outcomes_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('content_gr'),css_class = 'col-lg-6'),
                        Div(Field('content_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('delivery_gr'),css_class = 'col-lg-6'),
                        Div(Field('delivery_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),  
                    Row(
                        Div(Field('ict_gr'),css_class = 'col-lg-6'),
                        Div(Field('ict_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('bibliography_gr'),css_class = 'col-lg-6'),
                        Div(Field('bibliography_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(Field('evaluation_gr'),css_class = 'col-lg-6'),
                        Div(Field('evaluation_en'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                   
                    Row(
                        Div(Field('required_math'),css_class = 'col-lg-6'),
                        Div(Field('required_lab'),css_class = 'col-lg-6'),                                    
                        css_class="row"),
                    Row(
                        Div(HTML('<p></p><h5> Φόρτος Μαθήματος (Εβδομαδιαίος) </h5>'),css_class = 'row')
                    ),
                    Row(
                        Div(Field('weekly_hours'),css_class = 'col-lg-6'),
                        Div(Field('weekly_lab_hours'),css_class = 'col-lg-6'),
                        css_class="row"),
                    
                    Row(
                        Div(HTML('<p></p><h5> Φόρτος Μαθήματος (μέσα στο εξάμηνο) </h5>'),css_class = 'row')
                    ),                    
                    Row(
                        Div(Field('hours_lecturing'),css_class = 'col-lg-6'),
                        Div(Field('hours_lab'),css_class = 'col-lg-6'),
                        Div(Field('hours_project'),css_class = 'col-lg-6'),
                        Div(Field('hours_lab_prep'),css_class = 'col-lg-6'),
                        Div(Field('hours_study'),css_class = 'col-lg-6'),
                        css_class="row"),
                    Row(Div(HTML('<p></p>')),css_class='row'),
                    Row(Div(HTML('<p>Σύνολο Φόρτου από τις δραστηριότητες: </p>'),id='total'),css_class='row'),
                    Row(Div(HTML('<p>Σύνολο Φόρτου από τα ECTS: </p>'),id='totalects'),css_class='row'),
                                         
                    )

PUBLIC_COURSE_LAYOUT = Layout(
                    Row(Div(HTML('<h4> Στοιχεία Μαθήματος </h4>')),css_class="row"),                    
                    )

for field in PUBLIC_COURSE_FIELDS:
    PUBLIC_COURSE_LAYOUT.append(
        Row(
            Div(Field(field), css_class="row")
        )
    )

PUBLIC_COURSE_LAYOUT.append(
    Row(
        Div(HTML('<p></p><p></p></br><h4> Φόρτος μέσα στο Εξάμηνο (Ώρες)</h4>')), css_class="row")
    )

for field in PUBLIC_COURSE_FIELDS_H:
    PUBLIC_COURSE_LAYOUT.append(
        Row(
            Div(Field(field), css_class="row")
        )
    )

PUBLIC_COURSE_LAYOUT_EN = Layout(
                    Row(Div(HTML('<h4> Course Details </h4>')),css_class="row"),                    
                    )

for field in PUBLIC_COURSE_FIELDS_EN:
    PUBLIC_COURSE_LAYOUT_EN.append(
        Row(
            Div(Field(field), css_class="row")
        )
    )

PUBLIC_COURSE_LAYOUT_EN.append(
    Row(
        Div(HTML('<p></p><p></p></br><h4> Load within semester (Hours) </h4>')), css_class="row")
    )

for field in PUBLIC_COURSE_FIELDS_H:
    PUBLIC_COURSE_LAYOUT_EN.append(
        Row(
            Div(Field(field), css_class="row")
        )
    )


class CourseForm(ModelForm):

    class Meta:

        model = Course

        fields = COURSE_FIELDS
        labels = COURSE_LABELS

        widgets = {
            'assigned_to' : autocomplete.ModelSelect2Multiple(url='myprofile:staffmember-autocomplete')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hours_lecturing'].disabled=True
        self.fields['hours_lab'].disabled=True
        
        self.helper = FormHelper()
        self.helper.layout = COURSE_LAYOUT

    def clean(self):
        cleaned_data = super().clean()

        weekly_hours = cleaned_data['weekly_hours']
        weekly_lab_hours = cleaned_data['weekly_lab_hours']
        hours_study = cleaned_data['hours_study']
        hours_project = cleaned_data['hours_project']
        hours_lab_prep = cleaned_data['hours_lab_prep']
        ects_credits = cleaned_data['ects_credits']

        total_hours = (weekly_hours + weekly_lab_hours) * 13 + hours_study + hours_project + hours_lab_prep
        ects_hours = ects_credits * 25
        if ects_hours != total_hours:
            msg = 'Έχετε συμπληρώσει %6.2f ώρες φόρτου στις δραστηριότητες ενώ ο φόρτος που προκύπτει από τα ECTS είναι %6.2f ώρες. Παρακαλούμε διορθώστε τον επιμερισμό του φόρτου' %(total_hours, ects_hours)
            raise ValidationError(msg)

class StaffCourseForm(CourseForm):
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k in COURSE_DISABLED_FIELDS_STAFF:
            self.fields[k].disabled = True

        for k in COURSE_OBLIGATORY_FIELDS_STAFF:
            self.fields[k].required = True

class PublicCourseForm(CourseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k in self.fields:
            self.fields[k].disabled = True
        self.fields.pop('assigned_to')

        self.helper = FormHelper()
        self.helper.layout = PUBLIC_COURSE_LAYOUT

class PublicCourseFormEn(ModelForm):

    class Meta:
       
        model = Course

        fields = COURSE_FIELDS
        labels = COURSE_LABELS_EN

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k in self.fields:
            self.fields[k].disabled = True
        self.fields.pop('assigned_to')

        self.helper = FormHelper()
        self.helper.layout = PUBLIC_COURSE_LAYOUT_EN

        