from django.shortcuts import render, redirect, get_object_or_404 
from .models import Employee, Payslip, Account
from django.contrib import messages 


global_sort = 'name ↑'

account_signed_in = None

def home_page(request):
    return render(request, 'payroll_app/home.html')

def employee_page(request): 
    global account_signed_in
    global global_sort

    
    if account_signed_in == None:
        messages.warning(request,"You need to log in first", extra_tags='login')
        return redirect('login')
    else:
        if request.method == 'POST': #sort by button
            sort = request.POST.get('sort_by', 'name ↑')
            global_sort = sort
        else:
            sort = global_sort

        Employee.objects.filter(overtime_pay__isnull=True).update(overtime_pay=0.0)
        Employee.objects.filter(Allowance__isnull=True).update(Allowance=0.0)
        Employee.objects.filter(overtime_hours__isnull=True).update(overtime_hours=0.0)

        if '↑' in sort:
            field = sort.replace(' ↑', '').strip()
            employees = Employee.objects.all().order_by(field)
        else:
            field = sort.replace(' ↓', '').strip()
            employees = Employee.objects.all().order_by(f'-{field}')

        return render(request, 'payroll_app/employee_page.html', {
            'employees': employees,
        })



def create_employee(request):
    global account_signed_in

    if account_signed_in == None:
        messages.warning(request,"You need to log in first", extra_tags='login')
        return redirect('login')
    else:
        if request.method == "POST":
            name = request.POST.get("name")
            id_number = request.POST.get("id_number").strip()
            rate = request.POST.get("rate")
            Allowance = request.POST.get("Allowance")

            try:
                if not name or not id_number or not rate:
                    messages.error(request, "Please fill all necessary fields." , extra_tags='create_employee')
                    return redirect('create_employee')
                elif Employee.objects.filter(id_number=id_number).exists():  
                    messages.error(request, "The id number is already taken", extra_tags='create_employee')
                    return redirect('create_employee')
                else:
                    messages.success(request, "employee added!", extra_tags='employee_page')
                    Employee.objects.create(name=name, id_number=id_number, rate=rate, Allowance=Allowance if Allowance else 0)
                    return redirect('employee_page')
            except:
                messages.error(request, "Please fill all fields correctly.", extra_tags='create_employee')
                return redirect('create_employee')

        return render(request, 'payroll_app/create_employee.html')

def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    messages.success(request, "Employee deleted successfully.", extra_tags='employee_page')
    return redirect ('employee_page')

def update_employee(request, pk):
    global account_signed_in
    
    if account_signed_in == None: 
        messages.error(request, "You are not signed in yet!", extra_tag='login')
        return redirect('login')
    else:

        if(request.method=="POST"):
            employee = get_object_or_404(Employee, pk=pk)
            name = request.POST.get('name')
            id_number = request.POST.get('id_number').strip()
            rate = request.POST.get('rate')
            Allowance = request.POST.get('Allowance')

            if not name or not id_number or not rate:
                messages.error(request, "Name, ID Number, and Rate cannot be blank.")
                return render(request, 'payroll_app/update_employee.html', {'employee': employee})
            if Employee.objects.exclude(pk=pk).filter(id_number=id_number).exists():
                messages.error(request, "ID number is already taken.", extra_tags="update_employee")
                return render(request, 'payroll_app/update_employee.html', {'employee': employee})
            
            #update all fields
            Employee.objects.filter(pk=pk).update(
                name=name,
                id_number=id_number,
                rate=rate,
                Allowance=Allowance if Allowance else 0
            )
            messages.success(request, f"{name}'s info has been updated.")
            return redirect('employee_page')

        employee = get_object_or_404(Employee, pk=pk)
        return render(request, 'payroll_app/update_employee.html', {'employee': employee})
   

def reset_overtime(request,pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.overtime_pay = 0
    employee.overtime_hours = 0
    employee.save()
    messages.success(request, f"{employee.name}'s overtime had been resetted.")
    return redirect('employee_page')

      
        

    
def add_overtime(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        try:
            overtime_input = float(request.POST.get('overtime_hours', 0))
            # If overtime_pay is None, set it to 0.0 first
            if employee.overtime_pay is None:
                employee.overtime_pay = 0.0
            # Add the computed overtime pay to the current value
            overtime_rate = round((employee.rate / 160) * 1.5 * overtime_input, 5)
            employee.overtime_pay += overtime_rate
            employee.overtime_hours += overtime_input
            employee.save()
            messages.success(request, f"{overtime_input} hour(s) added to {employee.name}'s overtime.")
            return redirect('employee_page')
        except ValueError:
            messages.error(request, "Invalid input. Please enter a valid number.")
            return redirect('employee_page')  


def create_payslip(request):
    global account_signed_in

    if account_signed_in == None:
        messages.warning(request,"You need to log in first", extra_tags='login')
        return redirect('login')
    else:
        employees = Employee.objects.all()
        payslips = Payslip.objects.all()

        if request.method == "POST":
            id_number = request.POST.get("id_number")
            month = request.POST.get("month")
            year = request.POST.get("year")
            cycle = int(request.POST.get("cycle"))

            try:
                if not (id_number or month or year or cycle):
                    messages.error(request, "Please fill all necessary fields." , extra_tags='create_payslip')
                    return redirect('create_payslip')
                elif Payslip.objects.filter(id_number=id_number, month=month, year=year, pay_cycle=cycle).exists():  
                    messages.error(request, "The payslip already exists!", extra_tags='create_payslip')
                    return redirect('create_payslip')
                else:
                    messages.success(request, "Payslip has been successfully created!", extra_tags='create_payslip')
                    employee_id = Employee.objects.get(pk=id_number).id_number
                    rate = float(Employee.objects.get(pk=id_number).rate)
                    overtime = float(Employee.objects.get(pk=id_number).overtime_pay)
                    earnings_allowance = float(Employee.objects.get(pk=id_number).Allowance)
                    if cycle == 2:
                        deductions_health = rate*0.04
                        sss = rate*0.045
                        deductions_tax = ((rate/2)+earnings_allowance+overtime-((deductions_health)+(sss)))*0.2
                        total_pay = ((rate/2)+earnings_allowance+overtime-((deductions_health)+(sss)))-deductions_tax
                        if month in ['January','March','May','July','August','October','December']:
                            date_range = '16-31'
                            Payslip.objects.create(id_number_id=id_number, month=month, date_range=date_range, year=year, pay_cycle=cycle, rate=rate, earnings_allowance=earnings_allowance, deductions_tax=deductions_tax, deductions_health=deductions_health, pag_ibig=0, sss=sss, overtime=overtime, total_pay=total_pay)
                            Employee.objects.filter(pk=id_number).update(overtime_pay = 0, overtime_hours = 0)
                            return redirect('create_payslip')
                        elif month in ['April','June','September','November']:
                            date_range = '16-30'
                            Payslip.objects.create(id_number_id=id_number, month=month, date_range=date_range, year=year, pay_cycle=cycle, rate=rate, earnings_allowance=earnings_allowance, deductions_tax=deductions_tax, deductions_health=deductions_health, pag_ibig=0, sss=sss, overtime=overtime, total_pay=total_pay)
                            Employee.objects.filter(pk=id_number).update(overtime_pay = 0, overtime_hours = 0)
                            return redirect('create_payslip')
                        else:
                            date_range = '15-28'
                            Payslip.objects.create(id_number_id=id_number, month=month, date_range=date_range, year=year, pay_cycle=cycle, rate=rate, earnings_allowance=earnings_allowance, deductions_tax=deductions_tax, deductions_health=deductions_health, pag_ibig=0, sss=sss, overtime=overtime, total_pay=total_pay)
                            Employee.objects.filter(pk=id_number).update(overtime_pay = 0, overtime_hours =0)
                            return redirect('create_payslip')
                    else:
                        pag_ibig = 100
                        deductions_tax = (((rate/2)+earnings_allowance+overtime)-pag_ibig)*0.2
                        total_pay = (((rate/2)+earnings_allowance+overtime)-pag_ibig)-deductions_tax
                        if month in ['January','March','May','July','August','October','December']:
                            Payslip.objects.create(id_number_id=id_number, month=month, date_range='1-15', year=year, pay_cycle=cycle, rate=rate, earnings_allowance=earnings_allowance, deductions_tax=deductions_tax, deductions_health=0, pag_ibig=pag_ibig, sss=0, overtime=overtime, total_pay=total_pay)
                            Employee.objects.filter(pk=id_number).update(overtime_pay = 0, overtime_hours =0)
                            return redirect('create_payslip')
                        elif month in ['April','June','September','November']:
                            Payslip.objects.create(id_number_id=id_number, month=month, date_range='1-15', year=year, pay_cycle=cycle, rate=rate, earnings_allowance=earnings_allowance, deductions_tax=deductions_tax, deductions_health=0, pag_ibig=pag_ibig, sss=0, overtime=overtime, total_pay=total_pay)
                            Employee.objects.filter(pk=id_number).update(overtime_pay = 0, overtime_hours =0)
                            return redirect('create_payslip')
                        else:
                            Payslip.objects.create(id_number_id=id_number, month=month, date_range='1-14', year=year, pay_cycle=cycle, rate=rate, earnings_allowance=earnings_allowance, deductions_tax=deductions_tax, deductions_health=0, pag_ibig=pag_ibig, sss=0, overtime=overtime, total_pay=total_pay)
                            Employee.objects.filter(pk=id_number).update(overtime_pay = 0, overtime_hours =0)
                            return redirect('create_payslip')
                    
                    
            except:
                messages.error(request, "Please fill all fields correctly.", extra_tags='create_payslip')
                redirect('create_payslip')

        return render(request, 'payroll_app/create_payslip.html' , {'employees': employees, 'payslips':payslips})
    
def delete_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    payslip.delete()
    messages.success(request, "Payslip deleted successfully.", extra_tags='create_payslip')
    return redirect ('create_payslip')

def view_payslip(request, pk):
    global account_signed_in

    if account_signed_in == None:
        messages.warning(request,"You need to log in first", extra_tags='login')
        return redirect('login')
    else:
        payslip = get_object_or_404(Payslip, pk=pk)
        employee = get_object_or_404(Employee, id_number=payslip.id_number.id_number)
        cycle_rate = payslip.rate/2
        gross_pay = cycle_rate + payslip.earnings_allowance + payslip.overtime
        total_deductions = payslip.deductions_tax + payslip.deductions_health + payslip.sss
        return render(request, 'payroll_app/view_payslip.html', {'payslip':payslip, 'employee':employee, 'gross_pay':gross_pay, 'total_deductions':total_deductions, 'cycle_rate':cycle_rate})




def login(request):
    global account_signed_in  
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if account.password == password:
                account_signed_in = account.pk  
                return redirect('employee_page')  
            else:
                messages.warning(request, "Wrong password")
                return redirect('login')
        except Account.DoesNotExist:
            messages.warning(request, "Account does not exist")
            return redirect('login')
          


    if account_signed_in != None:
        pk = account_signed_in
        account = Account.objects.get(pk=pk)
        return render(request, 'payroll_app/login.html', {'account': account})
    else:
        return render(request, 'payroll_app/login.html')

def log_out(request): 
    global account_signed_in
    account_signed_in = None
    return redirect('login')

def manage_acc(request):
    global account_signed_in

    if account_signed_in == None:
        messages.warning(request,"You need to log in first", extra_tags='login')
        return redirect('login')
    else:
        pk = account_signed_in
        account = Account.objects.get(pk=pk)
        return render(request, 'payroll_app/manage_acc.html', {'account': account})

def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip().lower()
        password = request.POST.get('password')

        Account.objects.create(username=username, password=password)
        messages.success(request, "Account created successfully")
        return redirect('login')
    return render(request, 'payroll_app/sign_up.html')

def delete_account(request):
    Account.objects.filter(pk=request.user.pk).delete()
    messages.warning(request, "Account deleted.")
    return redirect('login')

def update_password(request):
    global account_signed_in

    if account_signed_in == None:
        messages.warning(request,"You need to log in first", extra_tags='login')
        return redirect('login')
    else:
        pk = request.session.get('pk')
        account = get_object_or_404(Account, pk=pk)

        if(request.method=='POST'):
            newpass1 = request.POST.get('newpass1')
            newpass2 = request.POST.get('newpass2')
            if newpass1 == newpass2:
                Account.objects.filter(pk=pk).update(password=newpass1)
                messages.success(request, "Password changed successfully, Don't forget it again :).")
                return redirect('login') 
            else: #give a warning that the newpassword is not the same
                messages.error(request, "they not the same man")

        return render(request, 'payroll_app/update_password.html', {'account': account})


def details_employee(request,pk):
    global account_signed_in

    if account_signed_in == None:
        messages.warning(request,"You need to log in first", extra_tags='login')
        return redirect('login')
    else:
        employee = get_object_or_404(Employee, pk=pk)
        payslip = Payslip.objects.filter(id_number=employee.pk)
        return render(request, 'payroll_app/details_employee.html', {'employee':employee, 'payslip':payslip})