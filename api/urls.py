from django.conf.urls import url
from api import views
from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token, verify_jwt_token)

urlpatterns = [

  url(r'^auth/get-token', obtain_jwt_token),
  url(r'^auth/verify-token', verify_jwt_token),
  url(r'^auth/refresh-token', refresh_jwt_token),
  url(r'^auth/login/$', views.LoginView.as_view()),
  url(r'^auth/register/$', views.UserRegisterAPIView.as_view()),
  url(r'^auth/patient/register/$', views.PatientRegisterAPIView.as_view()),
  url(r'^auth/medecin/register/$', views.MedecinRegisterAPIView.as_view()),
  url(r'^auth/request-password-reset/$',
      views.PasswordResetRequestView.as_view()),
  url(r'^auth/reset-password/$', views.PasswordResetView.as_view()),
  url(r'^auth/change-password/$', views.ChangePasswordView.as_view()),
  url(r'^auth/me/$', views.UserRetrieveView.as_view()),
  url(r'^auth/me-admin/$', views.AdminRetrieveView.as_view()),
  url(r'^auth/accountactivation/(?P<slug>[\w\-]+)/$',
      views.AccountActivationAPIView.as_view()),
  url(r'^auth/accountactivation/$',
      views.AccountActivationAPIListView.as_view()),
  url(r'^auth/passwordreset/(?P<slug>[\w\-]+)/$',
      views.PasswordResetAPIView.as_view()),
  url(r'^auth/passwordreset/$',
      views.PasswordResetAPIListView.as_view()),

  url(r'^reactive_user/(?P<email>[^@]+@[^@]+\.[^@]+)/$', views.UserReactivationAPIView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/suppression/$', views.SuppressionCompteByAdminAPIView.as_view()),
  url(r'^user/suppression/$', views.SuppressionAPIListView.as_view()),
  url(r'^users_deleted/$', views.UserDeletedAPIListView.as_view()),

  url(r'^users/$', views.UserAPIListView.as_view()),
  url(r'^users/(?P<slug>[\w\-]+)/$', views.UserAPIView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/details/$', views.UserDetailAPIView.as_view()),

  url(r'^user/admins/(?P<slug>[\w\-]+)/$', views.AdminUserAPIView.as_view()),
  url(r'^user/admins/$', views.AdminUserAPIListView.as_view()),

  url(r'^specialites/(?P<slug>[\w\-]+)/$', views.SpecialiteAPIView.as_view()),
  url(r'^specialites/$', views.SpecialiteAPIListView.as_view()),
  url(r'^import_specialites/$', views.ImportSpecialiteExcelView.as_view()),


  url(r'^callback/intech/$', views.CallbackIntechAPIView.as_view()),

  url(r'^newsletters/(?P<slug>[\w\-]+)/$', views.NewsletterAPIView.as_view()),
  url(r'^newsletters/$', views.NewsletterAPIListView.as_view()),

  url(r'^conditions/(?P<slug>[\w\-]+)/$', views.ConditionAPIView.as_view()),
  url(r'^conditions/$', views.ConditionAPIListView.as_view()),
  url(r'^cgu/$', views.CGUAPIListView.as_view()),

  url(r'^conversations/$', views.ConversationAPIListView.as_view()),
  url(r'^conversations/(?P<slug>[\w\-]+)/$', views.ConversationAPIView.as_view()),
  url(r'^mobile/user/(?P<slug>[\w\-]+)/conversations/$', views.ConversationByUserByMobileAPIListView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/conversations/$', views.ConversationByUserAPIListView.as_view()),
  url(r'^conversation/(?P<slug>[\w\-]+)/messages/$', views.MessagesByConversationAPIListView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/messages/$', views.MessageByUserAPIListView.as_view()),
  url(r'^messages/$', views.MessageAPIListView.as_view()),
  url(r'^messages/(?P<slug>[\w\-]+)/$', views.MessageAPIView.as_view()),




  

]
