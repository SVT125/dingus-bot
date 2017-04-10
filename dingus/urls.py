from django.conf.urls import url

from dingus import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
]