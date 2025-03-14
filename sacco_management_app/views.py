from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse,JsonResponse
from .models import UserCredentials, Member, ContactMessage, Loan,Product, Deposit, Withdraw,LoanType  # Ensure Member model is imported
from .models import MemberAccount,LoanRepayment, MemberBalance,Shares,Savings,SInvestment,IProduct, Insurance,Investment
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User  # Import Django's User model
from django.utils.timezone import now
from datetime import timedelta
from . import views
from django.views.decorators.csrf import csrf_exempt

# Create 
def adminpanel(request):
    return render(request,'admin.html')


def dashboard(request):
    approved_loans = Loan.objects.filter(status="Approved")
    return render(request, "dashboard.html", {"approved_loans": approved_loans})


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            # Save to database
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            
            # Show success message
            messages.success(request, "Your message has been sent successfully! We will get back to you soon.")
        else:
            # Show error message
            messages.error(request, "Failed to send message. Please fill in all fields.")

        return redirect('contact')  # Redirect to contact page

    return render(request, 'contact.html')

def membership(request):
    return render(request,'membership.html')

def auth_view(request):
    return render(request,'login-register.html')

def home(request):
    return render(request,'index.html')

def portfolio(request):
    return render(request,'portfolio-details.html')

def investments(request):
    return render(request,'investments.html')

def services(request):
    return render(request,'service-details.html')


def savings(request):
    return render(request,'savings.html')

def credits(request):
    return render(request,'credits.html')
    
def about(request):
    return render(request,'about.html')

def faq(request):
    return render(request,'faqs.html')

def terms(request):
    return render(request,'terms.html')

def privacy(request):
    return render(request,'privacy.html')

def financiallyadvisory(request):
    return render(request,'financialadvisory.html')

def loan(request):
    return render(request,'loanproduct.html')

def banking(request):
    return render(request,'banking.html')

def insurance(request):
    return render(request,'insurance.html')

def contact(request):
    return render(request,'contact.html')

def add_insurance(request):
    if request.method=='POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        product=Iproduct.objects.get(name=name)
        if product:
            messages.error(request,'the product exist suit another name')
            redirect('add_insurance')
        else:
            product=IProduct.objects.create(
                name=name,
                price=price,
            )
            return redirect('add_insurance')
    insurance=IProduct.objects.all()
    return render(request,'addinsurancetype.html',{
        'insurances': insurance
    })

def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        national_id = request.POST["national_id"]
        address = request.POST["address"]

        # Check if phone number already exists
        if Member.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered.")
            return redirect("register")

        # Check if email already exists
        if Member.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("register")

        # Check if national ID already exists
        if Member.objects.filter(national_id=national_id).exists():
            messages.error(request, "This National ID is already registered.")
            return redirect("register")

        new_member = Member.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            national_id=national_id,
            address=address
        )

        # Fetch the newly created account number
        member_account = MemberAccount.objects.get(member=new_member)

        return render(request, "accountconfirmation.html", {"account_number": member_account.account_number})

    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        account_number = request.POST.get('account_number', '').strip()
        password = request.POST.get('password', '').strip()

        if not account_number or not password:
            messages.error(request, "Account number and password are required.")
            return redirect('login')

        try:
            member_account = MemberAccount.objects.get(account_number=account_number)
            member = member_account.member
        except MemberAccount.DoesNotExist:
            messages.error(request, "Invalid account number. Please try again.")
            return redirect('login')

        # Authenticate using email (since Django User model uses username as email)
        user = authenticate(request, username=member.email, password=password)
        if user is not None:
            login(request, user)
            request.session['account_number'] = account_number  # Store account number in session
            return redirect('userpanel')
        else:
            messages.error(request, "Invalid password. Please try again.")
            return redirect('login')

    return render(request, 'login.html')



@login_required(login_url='login')
def userdashboard(request):
    account_number = request.session.get('account_number', None)

    if not account_number:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    try:
        member_account = MemberAccount.objects.get(account_number=account_number)
        member = member_account.member
        member_balance = MemberBalance.objects.get(member=member)  # 🔥 Fetch member balance

    except MemberAccount.DoesNotExist:
        messages.error(request, "Your account details are missing. Please contact support.")
        return redirect('error_page')
    except MemberBalance.DoesNotExist:
        member_balance = None  # Handle case where balance record doesn't exist
  
    products = IProduct.objects.all()  # Get all available products
    investment=Investment.objects.get(member_id=member.member_id)
    investmentvalue=investment.amount

    investments = SInvestment.objects.all()  # Fetch all investments from the database
    share=Shares.objects.get(account_number=account_number)
    saving=Savings.objects.get(account_number=account_number)
    savings=saving.amount
    memberbal=MemberBalance.objects.get(account_number=account_number)
    balance=memberbal.total_balance
    deposits=Deposit.objects.filter(member=member)
    withdrawals=Withdraw.objects.filter(member=member)

    return render(request, 'userdashboard.html', {
        'member': member,
        'member_account': member_account,
        'member_balance': member_balance ,# 🔥 Pass balance to template
        'totalshares': share.number_of_shares,
        'investments': investments,
        'products': products,
        'investmentvalue':investmentvalue,
         'savings':savings,
         'balance': balance,
         'dividents': memberbal.dividend_value,
         'deposits': deposits,
         'withdrawals': withdrawals,
    })


def setpassword(request):
    if request.method == "POST":
        account_number = request.POST["account_number"].strip()
        password = request.POST["password"].strip()
        confirm_password = request.POST["confirm_password"].strip()

        if password != confirm_password:
            return render(request, "setpassword.html", {"error": "Passwords do not match"})

        # Check if the MemberAccount exists
        try:
            member_account = MemberAccount.objects.get(account_number=account_number)
            member = member_account.member
        except MemberAccount.DoesNotExist:
            return render(request, "setpassword.html", {"error": "Account number not found"})

        # Create or update a Django User for authentication
        user, created = User.objects.get_or_create(username=member.email, defaults={
            "email": member.email,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "password": make_password(password),  # Hash password before saving
        })

        if not created:
            user.password = make_password(password)  # Update password if user exists
            user.save()

        messages.success(request, "Password set successfully! You can now log in.")
        return redirect("login")

    return render(request, "setpassword.html")


@csrf_exempt
def apply_loan(request):
    loan_type=''
    account_number=request.session.get('account_number')
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        loan_type2 = request.POST.get("loan_type")
        if loan_type2=='1':
            loan_type="business"
        elif loan_type2=='2':
            loan_type="personal"
        elif loan_type2=='3':
            loan_type="education"
        elif loan_type2=='4':
            loan_type="health"
        elif loan_type2=='5':
            loan_type="others"
        else:
            loan_type='none'
    
        account_Mumber=MemberAccount.objects.get(account_number=account_number)
        member=account_Mumber.member
        if member:   
            loanacc=Loan.objects.get(member=member)
            if loanacc:
                memberacc=MemberBalance.objects.get(member=member)
                if memberacc.total_balance>amount:
                    loanacc.amount=amount
                    loanacc.interest_rate=0.5
                    loanacc.member=member
                    loanacc.status='approved'
                    loanacc.loan_type=loan_type
                    loanacc.save()
                    messages.success(request,"loan is successfull")
                    return redirect('apply_loan')
                else:
                    messages.success(request,"loan is unsuccessfull your balance is low minimum !")
                    return redirect('apply_loan')
                
    
    return redirect('userpanel')


def make_repayment(request):
    account_number=request.session.get('account_number')
    
    if request.method == "POST":
        amount_paid = float(request.POST.get("loanAmount"))
        account_Mumber=MemberAccount.objects.get(account_number=account_number)
        member=account_Mumber.member   
        loanacc=Loan.objects.get(member=member)
        new_amount=float(loanacc.amount)-amount_paid
        loanacc.member=member
        loanacc.amount=new_amount
        loanacc.save()
        memberbal=MemberBalance.objects.get(account_number=account_number)
        balance=float(memberbal.total_balance)-amount_paid
        memberbal.total_balance=balance
        memberbal.loans_available=loanacc.amount
        memberbal.save()
        messages.success(request,"successfully paid ")
        return redirect('make_repayment')

    return redirect('userpanel')

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')

        if name and price:
            try:
                price = float(price)
                product = Product(name=name, price=price)
                product.save()
                messages.success(request, "Product added successfully!")
            except ValueError:
                messages.error(request, "Invalid price entered.")
        else:
            messages.error(request, "All fields are required.")

        return redirect('add_product')  # Redirect to the same page

    products = Product.objects.all().order_by('-date_added')
    return render(request, 'product.html', {'products': products})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import MemberAccount, Shares

@login_required
def manage_shares(request):
    # Retrieve the account number from the session
    account_number = request.session.get('account_number')

    # Ensure the user is authenticated
    if not account_number:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')
        
    
# Retrieve existing shares or create new ones
    
    if request.method == 'POST':
        action=''
        quantity = int(request.POST.get('quantity', 0))  # Default to 0 if quantity is missing
        quantity2 = int(request.POST.get('quantity2', 0))
        if quantity>quantity2:
            valuer=quantity
        else:
            valuer=quantity2
        share = Shares.objects.filter(account_number=account_number).first()
        if quantity2>0:
            if share:
                if share.number_of_shares>quantity2:
                    share.number_of_shares -= quantity2
                    share.save()
                    action='successfully sold: '
                    messages.success(request,'successfully selled shares')
                    redirect('manage_shares')
                else:
                    action='hush you have inssufficient shares to sell'
                    messages.success(request,'hush you have inssufficient shares to sell')
                    redirect('manage_shares')
            else:
                messages.success(request,'hush you have inssufficient or no shares to sell')
                
                redirect('manage_shares')
        elif quantity>0:
            memberacc=MemberAccount.objects.get(account_number=account_number)
            member=memberacc.member
            memberbal=MemberBalance.objects.get(member=member)
            total_balance=memberbal.total_balance
            sharesp=Product.objects.get(name="Shares")
            sharesprice=sharesp.price
            if (quantity*sharesprice)<total_balance:
                if share:
                    share.number_of_shares += quantity
                    share.save()
                    memberbal.total_balance=total_balance-(quantity*sharesprice)
                    memberbal.save()
                    messages.success(request,'successfully bought shares')
                    redirect('manage_shares')
                else:
                    Shares.objects.create(account_number=account_number, number_of_shares=quantity, share_value=35)
                    messages.error(request,'successfully bought shares')
                    redirect('manage_shares')
            else:
                messages.error(request,'insufficient funds on your account')
                redirect('manage_shares')
    share = Shares.objects.filter(account_number=account_number).first()
    memberacc=MemberAccount.objects.get(account_number=account_number)
    product=Product.objects.get(name='shares')
    memberacc.shares_value=(share.number_of_shares)*product.price
    membbal=MemberBalance.objects.get(account_number=account_number)
    membbal.shares_value=(share.number_of_shares)*product.price
    membbal.save()
    memberacc.save()
    return render(request, 'successpanel.html' , {'shares': share.number_of_shares,
    'action': action })


@login_required
def deposit_withdraw(request):
    valuer=0
    action="transacted"
    account_number = request.session.get('account_number')
   # Fetch the MemberAccount instance based on the account_number
    member_account = MemberAccount.objects.get(account_number=account_number)

# Access the related Member instance via the 'member' field in MemberAccount
    member = member_account.member

# Now you can access the phone number of the related Member
    phone = member.phone

    try:
        saving = Savings.objects.get(account_number=account_number)
    except Savings.DoesNotExist:
        saving = None
    except Savings.MultipleObjectsReturned:
        saving = None

    if request.method == 'POST':
        amount1 = int(request.POST.get('amount', 0))
        amount2 = int(request.POST.get('amount2', 0))
        phone2 = request.POST.get('phone', 0)
        if amount1>amount2:
            valuer+=amount1
            phone=phone
           
        elif amount2>amount1:
            valuer+=amount2
            phone=" withdrawn no to: "+phone2
            print(phone)
            

        # Handle Deposit
        if amount1 > 0:
            saving.amount += amount1
            saving.save()
            memberacc = MemberBalance.objects.get(account_number=account_number)
            memberacc.savings_amount = saving.amount
            memberacc.save()

            transacted=Deposit.objects.create(
            member = member,
            amount = amount1,
            description = 'Deposit transaction',
            )
            transacted.save()

            messages.success(request, 'Deposited successfully')
            return redirect('dw')  # Redirect after successful deposit

        # Handle Withdrawal
        elif amount2 > 0:
            memberacc = MemberBalance.objects.get(account_number=account_number)
            if memberacc.total_balance>amount2:
                saving.amount -= amount2
                saving.save()
                memberacc.savings_amount = saving.amount
                memberacc.save()
            
                messages.success(request, 'Withdrawn successfully')
                transacted=Withdraw.objects.create(
                member = member,
                amount = amount2,
                description = 'Withdrawal transaction',
                )
                transacted.save()
                return redirect('dw')  # Redirect after successful withdrawal
            else:
                messages.error(request, 'Withdrawn unsuccessfull : insufficient funds!')
                return redirect('dw')
    
    membbal=MemberBalance.objects.get(account_number=account_number)
    membbal.savings_amount=saving.amount
    membbal.save()
    newAmount = saving.amount if saving else 0  # Ensure you safely access saving.amount
    return render(request, "dwpanel.html", {
        'phone': phone,
        'savings': newAmount,
        'action': action
    })

def calculate_dividents(request):
    account_number=request.session.get('account_number')
    mebbal=MemberBalance.objects.get(account_number=account_number)
    product=Product.objects.get(name='dividents')
    divprice=product.price
    mebbal.dividend_value=(mebbal.shares_value)*divprice
    mebbal.total_balance=(mebbal.savings_amount+mebbal.dividend_value+mebbal.shares_value+mebbal.investment_value-mebbal.loans_available)
    mebbal.save()

    return redirect('userpanel')



def buy_investment(request):
    account_number=request.session.get('account_number')
    member_account=MemberAccount.objects.get(account_number=account_number)
    member=member_account.member
    investments=Investment.objects.get(member_id=member.member_id)
    if request.method == 'POST':
        investment_id = request.POST.get('investment_id')

        
        try:
            investment = SInvestment.objects.get(id=investment_id)
            if investments:
                memberbal=MemberBalance.objects.get(member=member)
                balance=memberbal.total_balance
                if memberbal.total_balance>investment.price:
                    investments.member = member
                    investments.amount = investment.price
                    investments.member_id=member.member_id
                    investments.save()
                    memberbal.total_balance=balance-investment.price
                    memberbal.investment_value=investment.price
                    memberbal.save()
               
            # You can also add the logic for processing the purchase here
            # For now, let's assume the purchase is successful and just show a message.
            
                    message = f"You have successfully bought {investment.name} for ${investment.price}!"
            
            # Generate a styled HTML response
                    html_response = f"""
                    <html>
                    <head>
                    <title>Purchase Confirmation</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f9f9f9;
                            color: #333;
                            margin: 0;
                            padding: 0;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 100px auto;
                            padding: 20px;
                            background-color: #fff;
                            border-radius: 8px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }}
                        h1 {{
                            color: #4CAF50;
                        }}
                        p {{
                            font-size: 1.2em;
                            margin: 20px 0;
                        }}
                        .btn {{
                            padding: 10px 20px;
                            background-color: #4CAF50;
                            color: white;
                            text-decoration: none;
                            font-size: 1em;
                            border-radius: 5px;
                            margin-top: 20px;
                            display: inline-block;
                            transition: background-color 0.3s;
                        }}
                        .btn:hover {{
                            background-color: #45a049;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Purchase Confirmation</h1>
                        <p>{message}</p>
                        <a href="/userpanel" class="btn">Return to Dashboard</a>
                    </div>
                </body>
            </html>
            """
                    return HttpResponse(html_response)
                else:
                    messages.error(request,'inssuffeiciend funds to buy product')
                    return redirect('userpanel')
        except SInvestment.DoesNotExist:
            return HttpResponse("Investment not found.", status=404)
    
    return redirect('investment_list')



def add_investment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')

        if name and price and description:
            # Create a new investment and save to the database
            try:
                investment = SInvestment.objects.create(
                    name=name,
                    price=price,
                    description=description
                )
                investment.save()
                messages.success(request, 'Investment added successfully!')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, 'Please fill out all fields.')

        return redirect('add_investment')  # Redirect after submitting the form to the same page
    
    return render(request, 'investment_form.html')




    

# View for purchasing insurance

from django.utils import timezone



@login_required
def purchase_insurance(request):
    if request.method == 'POST':
        # Get the product ID from the POST data
        product_id = request.POST.get('product_id')
        
        try:
            # Fetch the Product instance using the product ID
            product = IProduct.objects.get(id=product_id)
            
            # Get the current logged-in user
            account_number=request.session.get('account_number')
            # Ensure that the user has a MemberAccount associated
            memberbal=MemberBalance.objects.get(account_number=account_number)
            if memberbal.total_balance>product.price:
                # Create an Insurance instance with the correct Product object and Member
                insurance=Insurance.objects.get(account_number=account_number)
                if insurance:
                    insurance.product=product, 
                    insurance.start_date=timezone.now()
                    return redirect('userpanel')
                    messages.success(request,"insurance started successfully")
                else:

                    insurance = Insurance.objects.create(
                        account_number=account_number,  # Use the Member's account number
                        product=product, 
                    # The Product instance
                        start_date=timezone.now(),  # Automatically set the start date
                     )
                    messages.success(request,"insurance started successfully")
                    # Redirect or render success page after purchase
                    return redirect('userpanel')
            else:
                messages.error(request,'error cannot start insurance: top up your account !')
        except Product.DoesNotExist:
            # Handle the case where the product is not found
            error_message = "Product not found."
            return render(request, 'error.html', {'error': error_message})

    # If the request is not POST, redirect to the insurance list
    return redirect('userpanel')




def insurance_details(request):
    # Get the user's insurance from the database (example for the first insurance)
    insurance = Insurance.objects.first()

    if insurance:
        # Calculate the end_date dynamically
        end_date = insurance.start_date + timedelta(days=30)
        
        # Pass insurance and calculated end_date to the template
        return render(request, 'insurance_details.html', {
            'insurance': insurance,
            'end_date': end_date,
        })
    else:
        return render(request, 'insurance_details.html', {
            'error': 'No insurance found.',
        })



from django.shortcuts import render, redirect
from .models import LoanType

def loan_type_editor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        interest_rate = request.POST.get('interest_rate')
        description = request.POST.get('description')
        
        # Get the loan type if it exists, or create it if not
        loan_type, created = LoanType.objects.get_or_create(
            name=name,
            defaults={'interest_rate': interest_rate, 'description': description}
        )
        
        # If it already existed, update the fields
        if not created:
            loan_type.interest_rate = interest_rate
            loan_type.description = description
            loan_type.save()
        
        # Redirect back to the same page or to a success page
        return redirect('update_loan_type')
    loansrate=LoanType.objects.all()
        
    return render(request, 'loan_type_editor.html',{
        'loans': loansrate
    })

from django.shortcuts import render, get_object_or_404
from .models import Member, Deposit, Withdraw, Insurance
import json

def insurance_transactions_chart(request):
    account_number=request.session.get('account_number')
    account_mumber=MemberAccount.objects.get(account_number=account_number)
    member = account_mumber.member

    # Fetch deposits, withdrawals, and insurance payments
    deposits = Deposit.objects.filter(member=member)
    withdrawals = Withdraw.objects.filter(member=member)
    insurance_policies = Insurance.objects.filter(account_number=account_number)  # Assuming product has member

    # Format data for Chart.js
    transaction_data = [
        {"transaction_type": "Deposit", "amount": float(sum(d.amount for d in deposits))},
        {"transaction_type": "Withdraw", "amount": float(sum(w.amount for w in withdrawals))},
        {"transaction_type": "Insurance Payment", "amount": float(len(insurance_policies) * 1000)}  # Example amount
    ]

    return render(request, 'insurance_transaction_chart.html', {
        "member": member,
        "transaction_data": json.dumps(transaction_data)  # Pass data as JSON
    })

from datetime import date, timedelta
from .models import Member

def member_report(request):
    # Get all members
    members = Member.objects.all()

    # Members in SACCO for over 1 year
    

    one_year_ago = date.today() - timedelta(days=365)

    long_term_members = Member.objects.filter(join_date__lte=one_year_ago)

    memberbal=MemberBalance.objects.all()

    context = {
        'members': members,
        'long_term_members': long_term_members,
        'memberbal': memberbal,
    }

    return render(request, 'report1.html', context)

from django.shortcuts import render
from django.http import HttpResponse
from .models import Member

def member_list(request):
    members =MemberBalance.objects.all()
    return render(request, 'report2.html', {'members': members})

def download_pdf(request):
    return HttpResponse("PDF download functionality will be implemented later.")



def report3(request):
    loans=Loan.objects.all()
    return render(request, 'report3.html',{
        'loans' : loans,
    })

from django.shortcuts import render
from .models import Investment

def investment_reports(request):
    # Fetch all investments
    investments = Investment.objects.select_related("member").all()
    
    # Calculate total investments
    total_investments = sum(investment.amount for investment in investments)
    
    # Pass data to the template
    context = {
        "investments": investments,
        "total_investments": total_investments,
    }
    return render(request, "report4.html", context)

from django.shortcuts import render
from .models import Shares
from django.db.models import Sum
import json

def share_reports(request):
    # Get all share records
    shares = Shares.objects.all()

    # Calculate total shares owned
    total_shares = shares.aggregate(Sum('number_of_shares'))['number_of_shares__sum'] or 0

    # Prepare data for the Share Value Growth chart
    share_growth = list(shares.order_by('id').values_list('share_value', flat=True))  # Get share values
    share_growth = [float(value) for value in share_growth]  # Convert Decimal to float

    labels = [f"Record {i+1}" for i in range(len(share_growth))]  # Example labels

    context = {
        'shares': shares,
        'total_shares': total_shares,
        'labels': json.dumps(labels),  # Convert to JSON
        'values': json.dumps(share_growth),  # Convert list to JSON
    }

    return render(request, 'report5.html', context)



from datetime import datetime
from django.shortcuts import render
from .models import Insurance
def insurance_reports(request):
    # Get current date
    today = datetime.now()
    
    # Query active insurance policies (end date is in the future)
    active_insurance = Insurance.objects.filter(end_date__gte=today)
    
    # Query expired insurance policies (end date is in the past)
    expired_insurance = Insurance.objects.filter(end_date__lt=today)
    
    # Get all insurance claims
    
    
    context = {
        'active_insurance': active_insurance,
        'expired_insurance': expired_insurance,
        
    }
    return render(request, 'report6.html', context)

from django.shortcuts import render
from .models import Deposit, Withdraw
from django.db import models


def transaction_reports(request):
    deposits = Deposit.objects.all().order_by('-date')
    withdrawals = Withdraw.objects.all().order_by('-date')

    total_deposits = deposits.aggregate(total=models.Sum('amount'))['total'] or 0
    total_withdrawals = withdrawals.aggregate(total=models.Sum('amount'))['total'] or 0
    net_balance = total_deposits - total_withdrawals

    context = {
        'deposits': deposits,
        'withdrawals': withdrawals,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'net_balance': net_balance,
    }
    return render(request, 'report7.html', context)

from django.shortcuts import render
from .models import Member, Loan, Savings, MemberBalance

def member_query_view(request):
    query_results = None
    search_term = request.GET.get("search", "")

    if search_term:
        query_results = Member.objects.filter(
            first_name__icontains=search_term
        ) | Member.objects.filter(
            last_name__icontains=search_term
        ) | Member.objects.filter(
            email__icontains=search_term
        ) | Member.objects.filter(
            phone__icontains=search_term
        )

    context = {
        "query_results": query_results,
        "search_term": search_term
    }
    return render(request, "query_member.html", context)
from django.shortcuts import render
from .models import Loan
from datetime import datetime

def loan_search(request):
    query = request.GET.get('query', '')  
    filter_type = request.GET.get('filter', '')  
    loans = Loan.objects.all()  

    if filter_type == "loan_number":
        loans = loans.filter(loan_number__icontains=query)
    elif filter_type == "status":
        loans = loans.filter(status__iexact=query)
    elif filter_type == "amount":
        try:
            min_amount, max_amount = map(int, query.split('-'))
            loans = loans.filter(amount__gte=min_amount, amount__lte=max_amount)
        except ValueError:
            loans = Loan.objects.none()  
    elif filter_type == "repayment_date":
        loans = loans.filter(repayment_date=query)
    elif filter_type == "overdue":
        loans = loans.filter(due_date__lt=datetime.today(), status="Unpaid")

    return render(request, 'loan_search.html', {'loans': loans, 'query': query, 'filter_type': filter_type})

from django.shortcuts import render
from .models import Deposit, Withdraw
from datetime import datetime

def transaction_query(request):
    query = request.GET.get("transaction_id", "")
    transaction_type = request.GET.get("transaction_type", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    payment_method = request.GET.get("payment_method", "")

    transactions = []

    # Filter transactions based on user input
    if query:
        transactions = Deposit.objects.filter(transaction_id__icontains=query) | Withdraw.objects.filter(transaction_id__icontains=query)
    elif transaction_type:
        if transaction_type == "Deposit":
            transactions = Deposit.objects.all()
        elif transaction_type == "Withdrawal":
            transactions = Withdraw.objects.all()
    elif start_date and end_date:
        transactions = (Deposit.objects.filter(date__range=[start_date, end_date]) | 
                        Withdraw.objects.filter(date__range=[start_date, end_date]))
    elif payment_method:
        transactions = (Deposit.objects.filter(description__icontains=payment_method) | 
                        Withdraw.objects.filter(description__icontains=payment_method))

    context = {
        "transactions": transactions,
        "transaction_id": query,
        "transaction_type": transaction_type,
        "start_date": start_date,
        "end_date": end_date,
        "payment_method": payment_method,
    }

    return render(request, "transaction_query.html", context)
from django.shortcuts import render
from .models import Savings

def savings_query(request):
    query = request.GET.get("account_number", "")
    min_balance = request.GET.get("min_balance", "")
    max_balance = request.GET.get("max_balance", "")

    savings = Savings.objects.all()

    # Filter by account number
    if query:
        savings = savings.filter(account_number__icontains=query)

    # Filter by balance range
    if min_balance:
        savings = savings.filter(amount__gte=min_balance)
    if max_balance:
        savings = savings.filter(amount__lte=max_balance)

    context = {
        "savings": savings,
        "account_number": query,
        "min_balance": min_balance,
        "max_balance": max_balance,
    }

    return render(request, "savings_query.html", context)

from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime
from .models import Loan, Member  # Removed Transaction

def reports_view(request):
    # Total Loans Issued Today (using correct field)
    total_loans_today = Loan.objects.filter(start_date=datetime.today().date()).count()

    # Default value for deposits (since Transaction model doesn't exist)
    total_deposits_month = 0  

    # Members Who Haven’t Taken a Loan Yet
    members_without_loans = Member.objects.filter(loan__isnull=True).count()


    # Members with Outstanding Loans
    members_with_outstanding_loans = Loan.objects.filter(status="Unpaid").values("member").distinct().count()

    context = {
        "total_loans_today": total_loans_today,
        "total_deposits_month": total_deposits_month,
        "members_without_loans": members_without_loans,
        "members_with_outstanding_loans": members_with_outstanding_loans,
    }

    return render(request, "reports.html", context)
