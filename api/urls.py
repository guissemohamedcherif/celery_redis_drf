from django.conf.urls import url
from api import views
from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token, verify_jwt_token)

urlpatterns = [

  url(r'^auth/get-token', obtain_jwt_token),
  url(r'^auth/verify-token', verify_jwt_token),
  url(r'^auth/refresh-token', refresh_jwt_token),
  url(r'^auth/login/$', views.LoginView.as_view()),
#   url(r'^auth/register/$', views.UserRegisterAPIView.as_view()),
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
  url(r'^vendeur/inscription/$', views.VendeurRegisterAPIView.as_view()),
  url(r'^visiteur/inscription/$', views.VisiteurRegisterAPIView.as_view()),
  url(r'^vendeur/create/$', views.VendeurCreateAPIView.as_view()),
  url(r'^visiteur/create/$', views.VisiteurCreateAPIView.as_view()),
  url(r'^vendeurs/$', views.VendeurAPIListView.as_view()),
  url(r'^visiteurs/$', views.VisiteurAPIListView.as_view()),
  url(r'^vendeurs_blocked/$', views.VendeurBlockedAPIListView.as_view()),
  url(r'^vendeurs_blocked_mobile/$', views.VendeurBlockedMobileAPIListView.as_view()),
  url(r'^block_user/(?P<slug>[\w\-]+)/$', views.BlockUserAPIView.as_view()),
  url(r'^deblock_user/(?P<slug>[\w\-]+)/$', views.UnBlockUserAPIView.as_view()),
  url(r'^vendeurs_mobile/$', views.VendeurMobileAPIListView.as_view()),
  url(r'^visiteurs_mobile/$', views.VisiteurMobileAPIListView.as_view()),
  url(r'^visiteurs_blocked/$', views.VisiteurBlockedAPIListView.as_view()),
  url(r'^visiteurs_blocked_mobile/$', views.VisiteurBlockedMobileAPIListView.as_view()),

  url(r'^reactive_user/(?P<email>[^@]+@[^@]+\.[^@]+)/$', views.UserReactivationAPIView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/suppression/$', views.SuppressionCompteByAdminAPIView.as_view()),
  url(r'^user/suppression/$', views.SuppressionAPIListView.as_view()),
  url(r'^users_deleted/$', views.UserDeletedAPIListView.as_view()),

  url(r'^users/$', views.UserAPIListView.as_view()),
  url(r'^users/(?P<slug>[\w\-]+)/$', views.UserAPIView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/details/$', views.UserDetailAPIView.as_view()),

  url(r'^user/admins/(?P<slug>[\w\-]+)/$', views.AdminUserAPIView.as_view()),
  url(r'^user/admins/$', views.AdminUserAPIListView.as_view()),

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
  url(r'^mobile/messages/$', views.MessageMobileAPIListView.as_view()),
  
  
  url(r'^categories/$', views.CategorieAPIListView.as_view()),
  url(r'^categories/(?P<slug>[\w\-]+)/$', views.CategorieAPIView.as_view()),

  url(r'^produits/$', views.ProduitAPIListView.as_view()),
  url(r'^mobile/produits/$', views.ProduitMobileAPIListView.as_view()),
  url(r'^vendeur/(?P<slug>[\w\-]+)/produits/$', views.ProduitByVendeurAPIListView.as_view()),
  url(r'^mobile/vendeur/(?P<slug>[\w\-]+)/produits/$', views.ProduitByVendeurByMobileAPIListView.as_view()),
  url(r'^mobile/categories/$', views.CategorieByMobileAPIListView.as_view()),


  url(r'^produits/(?P<slug>[\w\-]+)/$', views.ProduitAPIView.as_view()),
  url(r'^visiteur/produits/$', views.ProduitVisiteurAPIListView.as_view()),

  url(r'^images/$', views.ImageAPIListView.as_view()),
  url(r'^images/(?P<slug>[\w\-]+)/$', views.ImageAPIView.as_view()),
  
  url(r'^vouchers/$', views.VoucherAPIListView.as_view()),
  url(r'^vouchers/(?P<slug>[\w\-]+)/$', views.VoucherAPIView.as_view()),
  url(r'^mobile/vouchers/$', views.VoucherMobileAPIListView.as_view()),
  
  url(r'^achats_vouchers/$', views.AchatVoucherAPIListView.as_view()),
  url(r'^achats_vouchers/(?P<slug>[\w\-]+)/$', views.AchatVoucherAPIView.as_view()),
  url(r'^mobile/achats_vouchers/$', views.AchatVoucherMobileAPIListView.as_view()),
  
  url(r'^cart_items/$', views.CartItemAPIListView.as_view()),
  url(r'^cart_items/(?P<slug>[\w\-]+)/$', views.CartItemAPIView.as_view()),

  url(r'^carts/$', views.CartAPIListView.as_view()),
  url(r'^carts/(?P<slug>[\w\-]+)/$', views.CartAPIView.as_view()),
  url(r'^cart/add/$', views.CartAddAPIListView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/cart/$', views.CartByUserAPIView.as_view()),
  url(r'^cart/(?P<slug>[\w\-]+)/clear/$', views.CartClearAPIView.as_view()),

  url(r'^orders/$', views.OrderAPIListView.as_view()),
  url(r'^orders/(?P<slug>[\w\-]+)/$', views.OrderAPIView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/canceled_orders/$', views.CanceledOrderByUserAPIListView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/orders/$', views.OrderByUserAPIListView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/canceled_orders_mobile/$', views.CanceledOrderByUserMobileAPIListView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/orders_mobile/$', views.OrderByUserMobileAPIListView.as_view()),
  url(r'^order_payment/(?P<slug>[\w\-]+)/$', views.OrderPaymentAPIView.as_view()),
  url(r'^vendeur/(?P<slug>[\w\-]+)/orders/$', views.OrderByVendeurAPIListView.as_view()),
  url(r'^vendeur/(?P<slug>[\w\-]+)/orders_mobile/$', views.OrderByVendeurMobileAPIListView.as_view()),
  url(r'^user/(?P<slug>[\w\-]+)/achat_voucher/$', views.AchatVoucherByUserAPIListView.as_view()),
 
  url(r'^config_points/$', views.ConfigPointAPIListView.as_view()),
  url(r'^config_points/(?P<slug>[\w\-]+)/$', views.ConfigPointAPIView.as_view()),
  
]
