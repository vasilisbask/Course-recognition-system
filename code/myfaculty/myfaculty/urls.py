"""
URL configuration for myfaculty project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from core.views import media_download

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("dashboard", RedirectView.as_view(url="/", permanent=False)),
    path("dashboard/", RedirectView.as_view(url="/", permanent=False)),
    path('media/<path:path>', media_download, name='media_download'),  
]

urlpatterns += i18n_patterns(
    path('api/', include('api.urls')),
    path("", include("myprofile.urls")),  
    path('associates/', include('associates.urls')),  
    path('projects/', include('projects.urls')),
    path('timesheets/', include('timesheets.urls')),  
    path('theses/', include('theses.urls')),      
    path('leaves/', include('leaves.urls')),
    path('curricula/', include('curricula.urls')),  
    path('', include('course_recognition.urls')),
    path('phdstuds/', include('phdstuds.urls')),
    path('phdapplications/', include('phdapplications.urls')),  
    path("accounts/", include("django.contrib.auth.urls")) ,
)


if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
