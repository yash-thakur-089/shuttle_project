from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, Wallet, Transaction, AdminCreditAssignment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'university_id', 'is_student', 'is_admin')
    list_filter = ('is_student', 'is_admin')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'university_id', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_student', 'is_admin', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'university_id', 'password1', 'password2', 'is_student', 'is_admin'),
        }),
    )

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'semester', 'date_created')
    search_fields = ('user__username', 'user__email', 'department')
    list_filter = ('department', 'semester')

class WalletAdmin(admin.ModelAdmin):
    list_display = ('student', 'balance', 'last_updated')
    search_fields = ('student__username', 'student__email')
    readonly_fields = ('last_updated',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'description', 'timestamp', 'remaining_balance')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('wallet__student__username', 'description')
    readonly_fields = ('timestamp',)

class AdminCreditAssignmentAdmin(admin.ModelAdmin):
    list_display = ('admin', 'student', 'amount', 'reason', 'timestamp')
    list_filter = ('admin', 'timestamp')
    search_fields = ('student__username', 'reason')

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(AdminCreditAssignment, AdminCreditAssignmentAdmin)