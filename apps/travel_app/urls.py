from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^main$', views.main),
    url(r'^profile/(?P<id>\d+)$', views.profile),
    url(r'^place/(?P<id>\w+)$', views.place),
    url(r'^visited/(?P<id>\w+)$', views.visited),
    url(r'^review/(?P<id>\w+)$', views.review),
]