from django.contrib import admin

# Register your models here.

from .models import *
# Register your models here.


# class RealProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'real_name', 'number', 'real_type')


admin.site.register(DataOrder)
admin.site.register(DataTicket)