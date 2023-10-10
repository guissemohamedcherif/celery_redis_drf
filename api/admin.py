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
admin.site.register(Offre)
admin.site.register(ModePaiement)
admin.site.register(Abonnement)
admin.site.register(Specialite)
admin.site.register(CallbackPayment)
admin.site.register(Notification)
admin.site.register(Medicament)
admin.site.register(Messagerie)