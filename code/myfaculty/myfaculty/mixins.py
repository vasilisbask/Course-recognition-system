class BackUrlMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['backurl'] = self.back_url
        return context
    
class PassRequestMixin:
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.request = self.request
        return form
    
class NextUrlMixin:
    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)