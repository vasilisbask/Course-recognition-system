from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic, View
from django.utils.translation import gettext_lazy as _
from myprofile.checks import is_secreteriat, is_staff_member, is_doctoral_student
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from scopes.utils import get_scoped_object_or_exc
from django.http import HttpResponse
from urllib.parse import unquote, quote
from myprofile.checks import can_download
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from django.core.exceptions import PermissionDenied

DEFAULT_CONTEXT_VALUES = {
    'master_headline' : None,
    'master_p' : None,
    'context_object_name' : 'objects',
    'table_id': 'objects',
    'page_length': 20,
    'table_title': _('Καταχωρήσεις'),
    'create_button': True,
    'create_url': None,
    'create_button_class': 'btn btn-primary',
    'create_button_icon': 'add_circle',
    'create_text': _('Νέα καταχώρηση'),
    'master_button': False,
    'master_url': None,
    'master_button_class': 'btn btn-success',
    'master_button_icon': 'account_circle',
    'master_text': _('Προσωπικά Στοιχεία'),
    'objects': [],
    'fields': [],
    'headers': [],
    'form_id' : 'crispyForm',
    
    'confirm_modal_title' : _('Επιβεβαίωση'),
    'confirm_modal_question' : _('Είστε σίγουροι ότι θέλετε να αποθηκεύσετε τις αλλαγές;'),
    'confirm_modal_cancel' : _('Όχι'),
    'confirm_modal_ok' : _('Ναι'),
    'confirm_modal' : False,

    'next': None,
    'back_url': None,

    'update_buttons': True,    
    'update_button_class': 'btn btn-primary',
    'update_button_icon': 'edit',
    'update_text': _('Ενημέρωση'),
    'update_url': None,
    'update_url_callable' : None,

    'extra_buttons' : False,
    'extra_button_class': 'btn btn-success',
    'extra_button_icon': 'radio_button_checked',
    'extra_text': _('Εικόνα'),
    'extra_url': None,

    'extra_buttons2' : False,
    'extra_button_class2': 'btn btn-secondary',
    'extra_button_icon2': 'person',
    'extra_text2': _('Στοχεία'),
    'extra_url2': None,

    'delete_buttons': False,    
    'delete_button_class': 'btn btn-danger',
    'delete_button_icon': 'delete_forever',
    'delete_text' : _('Διαγραφή'),    
    'delete_url' : None,
    
    'empty_text': _('Δεν υπάρχουν καταχωρήσεις'),
    'button_above_text' : '',
    'button_above_icon' : '',
    'button_above_classes' : "btn btn-primary",
    'headline_above' : '',
    'above_p' : '',
    'headline' : _('Ενημέρωση στοιχείων')
}

class GenericListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    template_name = 'core/list_objects.html'
    context_object_name = 'objects'
    model = None
    
    def set_defaults(self):
        for attr, value in DEFAULT_CONTEXT_VALUES.items():
            if not hasattr(self, attr):
                setattr(self, attr, value)

    def get_context_defaults(self):
        defaults = {}
        for attr in DEFAULT_CONTEXT_VALUES:
            defaults[attr] = getattr(self, attr, None)
        return defaults
    
    def get_update_url(self, obj):
        if self.update_url:
           return reverse_lazy(self.update_url, kwargs = {'pk' : obj.pk})
    
    def get_delete_url(self, obj):
        if self.delete_url:
            return reverse_lazy(self.delete_url, kwargs = {'pk' : obj.pk})
    
    def get_extra_url(self, obj):
        if self.extra_url:
            return reverse_lazy(self.extra_url, kwargs = {'pk' : obj.pk})
    
    def get_extra_url2(self, obj):
        if self.get_extra_url2:
            return reverse_lazy(self.extra_url2, kwargs = {'pk' : obj.pk})
    
    def get_create_url(self):
        if self.create_url:
            return reverse_lazy(self.create_url)
    
    def get_master_url(self):
        if self.master_url:
            return reverse_lazy(self.master_url)
    
    
    def __init__(self, *args, **kwargs):
        self.set_defaults()
        super().__init__(*args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        defaults = self.get_context_defaults()
        for k, v in defaults.items():
            if k not in context:
                context[k] = v
        context['create_url'] = self.get_create_url()
        context['master_url'] = self.get_master_url()

        if self.next:
            context['next'] = self.next
        else:
            context['next'] = self.request.path

        if self.back_url:
            context['back_url'] = self.back_url
        elif 'next' in self.request.GET:
            context['back_url'] = self.request.GET['next']

        for object in context[self.context_object_name]:
            object.update_url = self.get_update_url(object)
            object.delete_url = self.get_delete_url(object)
            object.extra_url = self.get_extra_url(object)
            object.extra_url2 = self.get_extra_url2(object)
        return context
    
    def test_func(self):
        return True
    
class ScopedSecListView(GenericListView):
    
    def test_func(self):
        return is_secreteriat(self.request.user)

    def get_queryset(self):
        return self.model.objects.sc_filter(user=self.request.user)
    

class GenericUpdateView(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = None
    template_name = 'core/show_object.html'
    form_class = None
    success_url = None
    back_url = None
    back_button = True

    def set_defaults(self):
        for attr, value in DEFAULT_CONTEXT_VALUES.items():
            if not hasattr(self, attr):
                setattr(self, attr, value)

    def get_context_defaults(self):
        defaults = {}
        for attr in DEFAULT_CONTEXT_VALUES:
            defaults[attr] = getattr(self, attr, None)
        return defaults
    
    def __init__(self, *args, **kwargs):
        self.set_defaults()
        if hasattr(self, 'success_url'):
            if isinstance(self.success_url, str):
                self.success_url = reverse_lazy(self.success_url)                
        super().__init__(*args, **kwargs)

    def get_delete_url(self, obj):
        if isinstance(self.delete_url, str):
            return reverse_lazy(self.delete_url, kwargs = {'pk' : obj.pk})
        else:
            return self.delete_url
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        kwargs['submit_button_text'] = self.update_text
        return kwargs
            
    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)
        defaults = self.get_context_defaults()
        for k, v in defaults.items():
            if k not in context:
                context[k] = v
        if self.back_button:
            context['back_url'] = self.request.GET.get('next', self.back_url)
        context['delete_url'] = self.get_delete_url(self.object)        
        context['success_url'] = self.get_success_url()

        return context

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)

    def test_func(self):
            return True
    
class GenericCreateView(UserPassesTestMixin, LoginRequiredMixin, generic.CreateView):
    
    model = None
    template_name = 'core/show_object.html'
    form_class = None
    success_url = None
    headline = _('Νέα καταχώρηση')
    back_url = None
    
    def set_defaults(self):
        for attr, value in DEFAULT_CONTEXT_VALUES.items():
            if not hasattr(self, attr):
                setattr(self, attr, value)
    
    def get_context_defaults(self):
        defaults = {}
        for attr in DEFAULT_CONTEXT_VALUES:
            defaults[attr] = getattr(self, attr, None)
        return defaults
    
    def __init__(self, *args, **kwargs):
        self.set_defaults()
        if hasattr(self, 'success_url'):
            if isinstance(self.success_url, str):
                self.success_url = reverse_lazy(self.success_url)
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user 
        return kwargs
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        defaults = self.get_context_defaults()
        for k, v in defaults.items():
            if k not in context:
                context[k] = v
        context['back_url'] = self.request.GET.get('next', self.back_url)
        context['headline'] = self.headline   
        return context

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)

    def test_func(self):
        return True
    
class GenericDeleteView(View):
    model = None
    success_url = None
    pk_url_kwarg = "pk"

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'success_url'):
            if isinstance(self.success_url, str):
                self.success_url = reverse_lazy(self.success_url)
        super().__init__(*args, **kwargs)
    
    def can_delete(self):
        return True

    def get(self, request, *args, **kwargs):
        
        obj = get_object_or_404(
            self.model,
            pk = kwargs[self.pk_url_kwarg]
        )
        if self.can_delete(obj):
            obj.delete()
        else:
            raise PermissionDenied
        
        next = request.GET.get('next')
        if next:
            return redirect(next)
        else:
            return redirect(self.success_url)

class Table:

    def __init__(self, objects = [], **kwargs):
        for k, v in DEFAULT_CONTEXT_VALUES.items():
            setattr(self, k, kwargs.get(k, v))
        
        self.objects = objects
        
        for object in self.objects:
            object.update_url = self.get_update_url(object)
            object.delete_url = self.get_delete_url(object)
            object.extra_url = self.get_extra_url(object)
            
    def get_update_url(self, obj):
        if self.update_url_callable:
            return self.update_url_callable(obj)
        
        if isinstance(self.update_url, str):
            return reverse_lazy(self.update_url, kwargs ={'pk' : obj.pk })
        else:
            return self.update_url
    
    def get_delete_url(self, obj):
        if isinstance(self.delete_url, str):
            return reverse_lazy(self.delete_url, kwargs ={'pk' : obj.pk })
        else:
            return self.delete_url
            
    def get_extra_url(self, obj):
        if isinstance(self.extra_url, str):
           return reverse_lazy(self.extra_url, kwargs ={'pk' : obj.pk })
        else:
            return self.extra_url
            
    def get_create_url(self):
        if isinstance(self.create_url, str):
           return reverse_lazy(self.create_url)
        elif self.create_url:
           return self.create_url
        
    
    def to_context(self):
        context = {}
        for k, v in DEFAULT_CONTEXT_VALUES.items():
            if hasattr(self, k):
                context[k] = getattr(self, k)
            else:
                context[k] = v
        
        context['objects'] = self.objects
        if self.create_button:
            context['create_url'] = self.get_create_url()
        
        return context  
    
class MultipleListView(GenericListView):

    tables = []
                    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = []
        for name, table in enumerate(self.tables):
            table_context = table.to_context()
            context['tables'].append(table_context)
        return context
    
    
class SecMultipleListView(MultipleListView):

    def test_func(self):
        return is_secreteriat(self.request.user)

class ScopedDeleteView(GenericDeleteView):

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'success_url'):
                if isinstance(self.success_url, str):
                    self.success_url = reverse_lazy(self.success_url)
        super().__init__(*args, **kwargs)
    
    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)
    
    def get(self, request, *args, **kwargs):
        obj = get_scoped_object_or_exc(
            self.model,
            user = self.request.user,
            pk = kwargs[self.pk_url_kwarg]
        )
        obj.delete()
        return redirect( self.get_success_url() )

    def test_func(self):
        return is_secreteriat(self.request.user)

class ScopedSecCreateView(GenericCreateView):

    def test_func(self):
        return is_secreteriat(self.request.user)
    
class ScopedSecUpdateView(GenericUpdateView):
    
    model = None
    template_name = 'core/show_object.html'
    form_class = None
    success_url = None
        
    def test_func(self):
        return is_secreteriat(self.request.user)
    
    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        obj.in_scope_or_403(self.request.user)
        return obj
    
class StaffUpdateView(GenericUpdateView):
                
    def test_func(self):
        return is_staff_member(self.request.user)
    
class StaffCreateView(GenericCreateView):
               
    def test_func(self):
        return is_staff_member(self.request.user)
    
class StaffMultipleListView(MultipleListView):

    def test_func(self):
        return is_staff_member(self.request.user)
    
class StaffListView(GenericListView):
    def test_func(self):
        return is_staff_member(self.request.user)

class DoctoralStudentUpdateView(GenericUpdateView):
                
    def test_func(self):
        return is_doctoral_student(self.request.user)
    
class DoctoralStudentCreateView(GenericCreateView):
               
    def test_func(self):
        return is_doctoral_student(self.request.user)
    
class DoctoralStudentMultipleListView(MultipleListView):

    def test_func(self):
        return is_doctoral_student(self.request.user)
    
class DoctoralStudentListView(GenericListView):
    def test_func(self):
        return is_doctoral_student(self.request.user)

class DoctoralStudentDeleteView(GenericListView):
    def test_func(self):
        return is_doctoral_student(self.request.user)

def media_download(request, path):
    path = unquote(path)  
    parts = path.split('/')
    
    # Expecting: phdstuds/<username>/<filename>
    if len(parts) < 2:
        return HttpResponse(status=404)
    
    
    allowed = can_download(parts, request.user)
        
    if allowed:
        full_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, path))
        if not full_path.startswith(str(settings.MEDIA_ROOT)):
           return HttpResponse(status=403)
        filename = parts[-1]
        
        if settings.DEBUG:
            # Development server: use Django FileResponse
            return FileResponse(open(full_path, 'rb'), as_attachment=True, filename=filename)
        else:
            # Production: use nginx X-Accel-Redirect
            encoded_path = quote(path)
            filename_encoded = quote(filename)
            response = HttpResponse()
            response["Content-Type"] = ""  # optional, let nginx set it
            response["Content-Disposition"] = f'attachment; filename="{filename_encoded}"'
            response["X-Accel-Redirect"] = f"/sec-media/{encoded_path}"
            print("X-Accel-Redirect:", f"/sec-media/{path}")
            return response    
    else:
        raise PermissionDenied()
    

    