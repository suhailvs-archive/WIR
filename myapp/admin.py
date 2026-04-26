from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Transaction, User

extrafields = ('balance','credit_limit',)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Other fields',{'fields':extrafields}),)
    list_display = ('username','first_name','credit_limit','balance','balance_from_txns')
    list_filter = ("is_active",)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Transaction)