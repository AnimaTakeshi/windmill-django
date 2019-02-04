from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.http import HttpResponseRedirect

def custom_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    else:
        return auth_views.login(request)
