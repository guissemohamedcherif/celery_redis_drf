# encoding: utf-8

from __future__ import unicode_literals

from django.contrib import admin


# Register your models here.
# Import our models module.
from api.models import *


admin.site.register(User)
admin.site.register(Product)
