"""
URL configuration for sacco_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .views import apply_loan
from .views import make_repayment


    


urlpatterns = [
    path('make-repayment/', make_repayment, name='make_repayment'),
    path('auth_view/', views.auth_view, name='auth_view'),
    path('', views.home,name='home'),
    path('portfolio/', views.portfolio,name='portfolio'),
    path('services/', views.services,name='services'),
    path('register/', views.register,name='register'),
     path('about/', views.about,name='about'),
      path('faqs/', views.faq,name='faqs'),
      path('terms/', views.terms,name='terms'),
      path('privacy/', views.privacy,name='privacy'),
      path('advisory/', views.financiallyadvisory,name='advisory'),
      path('loans/', views.loan,name='loans'),
       path('banking/', views.banking,name='banking'),
       path('insurance/',views.insurance,name='insurance'),
       path('contact/',views.contact,name='contact'),
       path('login/',views.login_view,name='login'),
        path('userpanel/',views.userdashboard,name='userpanel'),
       path("setpassword/", views.setpassword, name="setpassword"),
         path("membership/", views.membership, name="membership"),
         path("savings/", views.savings, name="savings"),
         path("credits/", views.credits, name="credits"),
          path("investments/", views.investments, name="investments"),
          path('add-product/', views.add_product, name='add_product'),
          path('manage-shares/', views.manage_shares, name='manage_shares'),
          path('dw/', views.deposit_withdraw, name='dw'),
          path('add_investment/', views.add_investment, name='add_investment'),
           path('buy_investment/', views.buy_investment, name='buy_investment'),
           path('purchase_insurance/', views.purchase_insurance, name='purchase_insurance'),
           path('insurance/details/', views.insurance_details, name='insurance_details'),
           path('claimdividents/',views.calculate_dividents,name='claimdividents'),
           path('apply_loan/',views.apply_loan,name='apply_loan'),
           path('insurance-transactions/', views.insurance_transactions_chart, name='insurance_transactions'),
            path('update_loan_type/', views.loan_type_editor , name='update_loan_type'),
            path('adminpanel/',views.adminpanel,name='adminpanel'),
            path('add_insurance/',views.add_insurance,name='add_insurance'),
            path('member-report/', views.member_report, name='member_report'),
            path('members/', views.member_list, name='member_list'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('report3/', views.report3, name='report3'),
    path("investment-reports/", views.investment_reports, name="investment_reports"),
    path('share-reports/', views.share_reports, name='share_reports'),
     path('insurance-reports/', views.insurance_reports, name='insurance_reports'),
     path('transactions/reports/', views.transaction_reports, name='transaction_reports'),
     path('query-member/', views.member_query_view, name='query-member'),
     path('loan-search/', views.loan_search, name='loan_search'),
     path('transactions/query/', views.transaction_query, name='transaction_query'),
     path('savings/query/', views.savings_query, name='savings_query'),
     path('reports_view/', views.reports_view, name='reports_view'),
           
]