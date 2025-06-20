from django.db import models

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=50, unique=True)
    rate = models.FloatField()
    overtime_pay = models.FloatField(null=True, blank=True)
    overtime_hours = models.FloatField(null=True, blank=True)
    Allowance = models.FloatField(null=True, blank=True)

    def getName(self):
        return self.name

    def getID(self):
        return self.id_number

    def getRate(self):
        return self.rate

    def getOvertime(self):
        return self.overtime_pay or 0

    def resetOvertime(self):
        self.overtime_pay = 0
        self.save()

    def resetOvertime_hours(self):
        self.overtime_hours = 0
        self.save()

    def getAllowance(self):
        return self.Allowance or 0

    def __str__(self):
        return f"pk: {self.getID()}, rate: {self.getRate()}"


class Payslip(models.Model):
    id_number = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    date_range = models.CharField(max_length=50)
    year = models.CharField(max_length=4)
    pay_cycle = models.IntegerField()
    rate = models.FloatField()
    earnings_allowance = models.FloatField()
    deductions_tax = models.FloatField()
    deductions_health = models.FloatField()
    pag_ibig = models.FloatField()
    sss = models.FloatField()
    overtime = models.FloatField()
    total_pay = models.FloatField()

    def getIDNumber(self):
        return self.id_number.id_number

    def getMonth(self):
        return self.month

    def getDate_range(self):
        return self.date_range

    def getYear(self):
        return self.year

    def getPay_cycle(self):
        return self.pay_cycle

    def getRate(self):
        return self.rate

    def getCycleRate(self):
        return self.rate / 2

    def getEarnings_allowance(self):
        return self.earnings_allowance

    def getDeductions_tax(self):
        return self.deductions_tax

    def getDeductions_health(self):
        return self.deductions_health

    def getPag_ibig(self):
        return self.pag_ibig

    def getSSS(self):
        return self.sss

    def getOvertime(self):
        return self.overtime

    def getTotal_pay(self):
        return self.total_pay

    def __str__(self):
        return (f"pk: {self.pk}, Employee: {self.getIDNumber()}, "
                f"Period: {self.getMonth()} {self.getDate_range()}, {self.getYear()}, "
                f"Cycle: {self.getPay_cycle()}, Total Pay: {self.getTotal_pay()}")

class Account(models.Model):
    username = models.CharField(max_length=300)
    password = models.CharField(max_length=300)
    objects = models.Manager()

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def __str__(self):
        return str(self.pk) + ": " + self.username