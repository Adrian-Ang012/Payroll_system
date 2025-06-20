"""
URL configuration for Lazapee project.

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
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('view_employee/', views.employee_page, name='employee_page'), 
    path('create_employee/', views.create_employee, name='create_employee'),
    path('employee/update/<int:pk>/', views.update_employee, name='update_employee'),
    path('employee/delete/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('employee/add_overtime/<int:pk>/', views.add_overtime, name='add_overtime'),
    path('employee/reset_overtime/<int:pk>/', views.reset_overtime, name='reset_overtime'),
    path('create_payslip/', views.create_payslip, name='create_payslip'),
    path('delete_payslip/delete/<int:pk>', views.delete_payslip, name='delete_payslip'),
    path('view_payslip/<int:pk>', views.view_payslip, name='view_payslip'),
    path('', views.login, name='login'),
    path('home/', views.home_page, name='home'),
    path('manage_acc/', views.manage_acc, name='manage_acc'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('update_password/', views.update_password, name='update_password'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('details_employee/<int:pk>/', views.details_employee, name='details_employee'),
    path('logout/', views.log_out, name='log_out')

]