"""
URL configuration for questoes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# View para redirecionar a raiz para a aplicação questoes
def redirect_to_questoes(request):
    return redirect('home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_questoes, name='root'),  # Redireciona a raiz para questoes
    path('questoes/', include('questoes.urls')),  # Inclui todas as URLs do app questoes
]
