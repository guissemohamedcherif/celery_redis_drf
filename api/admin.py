# encoding: utf-8

from __future__ import unicode_literals

from django.contrib import admin


# Register your models here.
# Import our models module.
from api.models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources


# Register our "Message" model with the Django Admin/


# class UserAdmin(admin.ModelAdmin):
#     readonly_fields = ('date_joined',)
#     list_display = ('email', )

class UserResource(resources.ModelResource):

    class Meta:
        model = User


class UserAdmin(ImportExportModelAdmin):
    readonly_fields = ('date_joined',)
    list_display = ('email', )
    resource_class = UserResource


admin.site.register(User)
admin.site.register(ModePaiement)
admin.site.register(CallbackPayment)
admin.site.register(Notification)
admin.site.register(Voucher)
admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(Image)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Contact)
admin.site.register(ResponseContact)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Saving)
admin.site.register(ConfigPoint)
admin.site.register(Signalement)