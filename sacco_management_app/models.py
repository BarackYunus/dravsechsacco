from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils.timezone import now
# Create your models here.
from django.contrib.auth.hashers import make_password
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import timedelta
from django.utils import timezone
import uuid


class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class MemberAccount(models.Model):
    account_number = models.CharField(max_length=8, unique=True, editable=False)
    member = models.OneToOneField(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f"Account {self.account_number} - {self.member.first_name} {self.member.last_name}"


# Auto-generate an 8-digit account number


# Auto-generate an 8-digit account number and initialize balances with zero
@receiver(post_save, sender=Member)
def create_member_account(sender, instance, created, **kwargs):
    if created:
        # Create Account Number
        last_account = MemberAccount.objects.order_by('-account_number').first()
        if last_account and last_account.account_number.isdigit():
            new_account_number = str(int(last_account.account_number) + 1).zfill(8)
        else:
            new_account_number = "10000000"  # Start from 10000000

        # Create Member Account
        member_account = MemberAccount.objects.create(
            member=instance,
            account_number=new_account_number
        )

        # Initialize MemberBalance with zero values
        MemberBalance.objects.create(
            member=instance,
            account_number=new_account_number,
            savings_amount=0,
            dividend_value=0,
            shares_value=0,
            investment_value=0,
            loans_available=0,
            total_balance=0
        )

        # Initialize related fields (e.g., Savings, Investments, etc.)
        Savings.objects.create(
            member=instance,
            account_number=new_account_number,
            amount=0
        )

        Investment.objects.create(
            member=instance,
            amount=0,
            investment_date=timezone.now(),
            return_rate=5.0,  # You can adjust this default if needed
            maturity_date=timezone.now() + timedelta(days=365)  # Example of default maturity date
        )

        Shares.objects.create(
            member=instance,
            account_number=new_account_number,
            number_of_shares=0,
            share_value=0
        )

        # Optionally, you can initialize Loans with a default value or leave them empty
        Loan.objects.create(
            member=instance,
            amount=0,
            loan_type='business',  # Default loan type
            interest_rate=0,
            start_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=90),
            status='Pending'
        )

        # Create initial User Credentials (this can be done if you have login mechanisms)
        UserCredentials.objects.create(
            member_account_number=new_account_number,
            password_hash='hashed_password'  # You should add real password handling
        )
        
        Insurance.objects.create(
            account_number=member_account.account_number,  # Use account number from MemberAccount
            product='null',  # Ensure this is a valid Product objects
            start_date=timezone.now(),  # Set start date to the current time
            end_date=timezone.now() + timedelta(days=30)  # Set end_date to 30 days from the start date
        )






class MemberBalance(models.Model):
    member = models.OneToOneField('Member', on_delete=models.CASCADE)
    account_number = models.CharField(max_length=8, unique=True, editable=False)
    savings_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dividend_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shares_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    investment_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loans_available = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def update_balance(self):
        """ Automatically updates balance based on all financial values. """
        loans_sum = Loan.objects.filter(member=self.member, status='Approved').aggregate(models.Sum('amount'))['amount__sum'] or 0
        savings_sum = Savings.objects.filter(member=self.member).aggregate(models.Sum('amount'))['amount__sum'] or 0
        investment_sum = Investment.objects.filter(member=self.member).aggregate(models.Sum('amount'))['amount__sum'] or 0

        self.savings_amount = savings_sum
        self.investment_value = investment_sum
        self.loans_available = loans_sum

    # Now, adding all fields together to calculate total_balance
        self.total_balance = (
            self.savings_amount +
            self.dividend_value +
            self.shares_value +
            self.investment_value +
            self.loans_available  # Include this if loans should be added, otherwise subtract if it's a liability
        )

        self.save()


    def __str__(self):
        return f"Balance for {self.member.first_name} ({self.account_number})"


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_type = models.CharField(
        max_length=20, 
        choices=[
            ('business', 'Business Loan'),
            ('personal', 'Personal Help Loan'),
            ('education', 'Education Loan'),
            ('health', 'Health Loan'),
            ('others', 'Others'),
        ],
        default='business'
    )
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=15, 
        choices=[('Pending', 'Pending'), ('Approved', 'approved'), ('Paid', 'Paid')],
        default='Pending'
    )

    def save(self, *args, **kwargs):
        """ Automatically set interest rate & due date before saving. """
        loan_interest_rates = {
            'business': 10.0,  
            'personal': 8.0,   
            'education': 5.0,  
            'health': 4.0,     
            'others': 6.0,     
        }
        if self.loan_type and not self.interest_rate:
            self.interest_rate = loan_interest_rates.get(self.loan_type, 5.0)

        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=90)  

        super().save(*args, **kwargs)

    def approve_loan(self):
        """ Deduct loan amount from balance upon approval """
        try:
            member_balance = self.member.memberbalance  
            loan_limit = self.get_loan_limit(member_balance.total_balance)

            if self.amount <= loan_limit:  # Check eligibility
                member_balance.total_balance -= self.amount
                member_balance.loans_available += self.amount
                member_balance.save()
                
                self.status = 'Approved'
                self.save()
                return True
        except MemberBalance.DoesNotExist:
            pass
        return False  # Not enough balance

    def get_loan_limit(self, account_balance):
        """ Returns the loan limit based on the loan type """
        limits = {
            'business': 0.7,
            'personal': 0.5,
            'education': 0.4,
            'health': 0.35,
            'others': 0.3,
        }
        return limits.get(self.loan_type, 0.3) * account_balance

    def __str__(self):
        return f"Loan {self.loan_id} - {self.member.first_name} ({self.loan_type})"


class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Increase balance when repayment is made """
        super().save(*args, **kwargs)
        try:
            member_balance = self.loan.member.memberbalance  
            member_balance.total_balance += self.amount_paid
            member_balance.save()
        except MemberBalance.DoesNotExist:
            pass

    def __str__(self):
        return f"Repayment for Loan {self.loan.loan_id} - Ksh. {self.amount_paid}"



class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Shares(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    account_number = models.CharField(max_length=8, unique=True)
    number_of_shares = models.PositiveIntegerField(default=0)
    share_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.member.first_name} - {self.number_of_shares} shares"


# ------------------------------
# MEMBER SAVINGS MODEL
# ------------------------------
class Savings(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    account_number = models.CharField(max_length=8, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Savings {self.id} - {self.member.first_name} {self.member.last_name}"

# ------------------------------
# MEMBER INVESTMENTS MODEL
# ------------------------------
class Investment(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    investment_date = models.DateTimeField(auto_now_add=True)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)  # Default 5% ROI
    maturity_date = models.DateField()

    def __str__(self):
        return f"Investment {self.id} - {self.member.first_name}"

    def calculate_return(self):
        """Calculate expected returns based on investment amount and return rate."""
        return (self.amount * self.return_rate) / 100


# ------------------------------
# NOTIFICATIONS MODEL (Alerts, Reminders)
# ------------------------------
NOTIFICATION_TYPES = [
    ('Loan Approved', 'Loan Approved'),
    ('Payment Due', 'Payment Due'),
    ('Late Payment Penalty', 'Late Payment Penalty'),
    ('General', 'General'),
]

class Notification(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.id} - {self.notification_type}"

# ------------------------------
# SUPPORT TICKETS MODEL
# ------------------------------
TICKET_STATUS = [
    ('Open', 'Open'),
    ('Resolved', 'Resolved'),
    ('Closed', 'Closed'),
]

class SupportTicket(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=TICKET_STATUS, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.subject} ({self.status})"



class ContactMessage(models.Model):
    id = models.AutoField(primary_key=True)  # ✅ Primary Key
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # ✅ Auto timestamp

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"







class UserCredentials(models.Model):
    member_account_number = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)

    def __str__(self):
        return self.member_account_number

class LatePayment(models.Model):
    late_id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    days_late = models.IntegerField(default=0)
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.days_late = (now().date() - self.due_date).days if self.due_date else 0
        self.penalty_amount = self.amount_due * 0.05 * self.days_late if self.days_late > 0 else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Late Payment {self.late_id} - Loan {self.loan.loan_id}"



class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - Loan {self.loan.id}"




class SInvestment(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.models import User

class IProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Insurance Model


class Insurance(models.Model):
    account_number = models.CharField(max_length=8, unique=True, editable=True, default="00000000")
    product = models.ForeignKey(IProduct, on_delete=models.CASCADE, default=None)  # Keep this for linking to the product
    start_date = models.DateTimeField(auto_now_add=True)  # Automatically set when insurance is created
    end_date = models.DateTimeField(null=True, blank=True)  # This can be set manually or calculated later

    def save(self, *args, **kwargs):
        # If end_date is not set, calculate it as 30 days after the start_date
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Insurance for {self.product.name}"

# ------------------------------
# TRANSACTIONS MODEL (Deposit, Withdrawal, Loan Repayment)
# ------------------------------


class Deposit(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=12, unique=True, editable=False)
    description = models.TextField(blank=True, null=True, default='Deposit transaction')
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        prefix = 'DEP'
        unique_id = str(uuid.uuid4().int)[:6]  # Generate a 6-digit unique number
        return f"{prefix}{unique_id}"
    
    def __str__(self):
        return f"{self.member.username} - Deposit - {self.amount} Ksh ({self.transaction_id})"

class Withdraw(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=12, unique=True, editable=False)
    description = models.TextField(blank=True, null=True, default='Withdrawal transaction')
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        prefix = 'WD'
        unique_id = str(uuid.uuid4().int)[:6]  # Generate a 6-digit unique number
        return f"{prefix}{unique_id}"
    
    def __str__(self):
        return f"{self.member.username} - Withdrawal - {self.amount} Ksh ({self.transaction_id})"



class LoanType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Loan type name as identifier
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)  # Interest rate percentage
    description = models.TextField(blank=True, null=True, default=None)  # Allow null description
    
    def __str__(self):
        return f"{self.name} - {self.interest_rate}%"
