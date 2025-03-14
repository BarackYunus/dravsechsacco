from django.contrib import admin

# Register your models here.
from .models import (
    Member, MemberAccount, UserCredentials,
    Savings, Investment, Notification, SupportTicket, ContactMessage,
    Loan, LatePayment, Payment
)




# Register models
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'status', 'join_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('status', 'join_date')

@admin.register(MemberAccount)
class MemberAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'member')

@admin.register(UserCredentials)
class UserCredentialsAdmin(admin.ModelAdmin):
    list_display = ('member_account_number',)

@admin.register(Savings)
class SavingsAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'deposit_date')

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'return_rate', 'investment_date', 'maturity_date')



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('member', 'notification_type', 'message', 'is_read', 'timestamp')
    list_filter = ('notification_type', 'is_read')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('member', 'subject', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp')
    search_fields = ('name', 'email', 'subject')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'interest_rate', 'start_date', 'due_date', 'status')
    list_filter = ('status', 'start_date', 'due_date')

@admin.register(LatePayment)
class LatePaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'due_date', 'amount_due', 'days_late', 'penalty_amount')
    list_filter = ('due_date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount_paid', 'payment_date')
