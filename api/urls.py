from django.urls import re_path
from api import views

urlpatterns = [

  re_path(r'^auth/login/$', views.LoginView.as_view()),
  re_path(r'^auth/register/$', views.UserRegisterAPIView.as_view()),
  re_path(r'^products/$', views.ProductAPIListView.as_view()),
  re_path(r'^products/(?P<slug>[\w\-]+)/$', views.ProductAPIView.as_view()),

]
