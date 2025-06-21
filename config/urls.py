"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from vault.views import RegisterView, health_check
from django.shortcuts import redirect


def redirect_to_login(request):
    """
    given a request if no path is given the default will be the login page
    """
    return redirect("login", permanent=False)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("cards/", include("vault.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", RegisterView.as_view(), name="register"),
    path("", redirect_to_login),
    path("healthz/", health_check, name="healthz"),
]
