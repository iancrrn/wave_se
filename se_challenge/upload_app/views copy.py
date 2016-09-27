# Ian Carreon, iancrrn@gmail.com
# August 27, 2016

# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm

# from .models import <model_name>
# Employee
# Expense
# ZipCode
# TaxName
# Hobby
# Category

from .models import *

import csv
from datetime import date

from django.db.models import Count
from django.db.models import F, FloatField, Sum

import calendar

# helper function
# Option: place this function is some file and do something like
# from somefile import handle_uploaded_file
def handle_uploaded_file(f):
    """
    http://stackoverflow.com/questions/3305926/python-csv-string-to-array
up vote
108
down vote
accepted
I would use StringIO:

import StringIO
import csv

f = StringIO.StringIO(scsv)
reader = csv.reader(f, delimiter=',')
for row in reader:
    print '\t'.join(row)
simplier version with split() on newlines:

reader = csv.reader(scsv.split('\n'), delimiter=',')
for row in reader:
    print '\t'.join(row)
Or you can simply split this string into lines using \n as separator, and then split each line into values, but this way you must be aware of quoting, so using csv module is preferred.    
  """
    
    """
    
    
    """
        # for large files e.g. ~ 2GB may be we could chunk the file
        for chunk in f.chunks():
            do_something_with_the(chunk)
    """
    """
    How to handle long running asyncronous tasks: threading/multiprocessing, Celery/Redis, AWS SQS...
    """
    print 'f: ', f
    
    
    for chunk in f.chunks():
        print 'chunk: ', chunk
        print 'type:  ', type(chunk)
        csvreader = csv.reader(chunk)

        # This skips the first row (i.e. header) of the CSV file.
        next(csvreader)

        for row in csvreader:
            # do stuff with each row...
            #print 'row: ', row
            
            0/0
        #destination.write(chunk)    

    csvreader = csv.reader(f)

    # This skips the first row (i.e. header) of the CSV file.
    next(csvreader)

    for row in csvreader:
        # do stuff with each row...
        
        # remove any whitespace
        print 'row: ', row
        
        row = [i.strip() for i in row]

        print 'row: ', row
        0/0

        # Extract the expense item part
        expense_date = row[0].split('/') # extract year, month, day
        year = int(expense_date[2])
        month = int(expense_date[0])
        day = int(expense_date[1])
        
        category = row[1]
        description = row[4]
        
        # work with integers - avoid issues working with floats
        # convert to cents (i.e. multiply by 100)
        pre_tax_amount = int(float(row[5].replace(',', '')) * 100)
        tax_name = row[6]
        tax_amount = int(float(row[7].replace(',', '')) * 100)
        total_amount = int(pre_tax_amount + tax_amount)
                
        # Extract employee part
        employee_name = [i.strip() for i in row[2].split()]
        first_name = employee_name[0]
        last_name = employee_name[1]
        
        
        # break up address into street, city, state and zipcode
        # e.g. 1600 Amphitheatre Parkway, Mountain View, CA 94043
        address = row[3].split(',')
        
        street = address[0].strip()
        city = address[1].strip()
        state_and_zipcode = address[2].strip()
        
        temp = state_and_zipcode.split(' ')
        state = temp[0].strip()
        zipcode = temp[1].strip()
        
        
        """
class Employee(models.Model):
    
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    street = models.CharField(max_length=90)
    zipcode = models.ForeignKey('ZipCode')

    class Meta:
        unique_together = ("first_name", "last_name", "street")
                
class ZipCode(models.Model):
    zipcode = models.CharField(max_length=10, primary_key = True) # Make this the PK since zipcodes are unique
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    
class TaxName(models.Model):
    tax_name = models.CharField(max_length=30)

class Category(models.Model):
    name = models.CharField(max_length=30)
    
class Expense(models.Model):
    date = models.DateField()    
    description = models.CharField(max_length=90)
    
    pre_tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    tax_name = models.ForeignKey(TaxName)
    category = models.ForeignKey(Category)
    employee = models.ForeignKey(Employee) #, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ("date", "category", "description", "pre_tax_amount", "employee")
    
class Hobby(models.Model):
    employee = models.ForeignKey(Employee) #, on_delete=models.CASCADE)
        
        
        """
        
        
        # if employee already in the database then use that otherwise create a new entry
        employee, created = Employee.objects.get_or_create(first_name=first_name, last_name=last_name, address=address)

        # if this expense item is already assigned to this employee then do nothing else create a new expense item for this employee
        expense_item, created = ExpenseItem.objects.get_or_create(date=date(year, month, day), category=category, description=description, 
                                pre_tax_amount=pre_tax_amount, tax_name=tax_name, tax_amount=tax_amount, total_amount=total_amount, employee=employee)
                                

def upload_file(request):
    
    # used for the data to return to the template
    data = []
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            
            try:
                handle_uploaded_file(request.FILES['file'])                
            # catch all for now
            # but depending on the error we can bow out gracefully or continue
            # i.e if exception is an IntegrityError then continue...
            # i.e if list index out of range error then stop - possibly invalid CSV file
            except Exception as e: 
                return render(request, 'upload.html', {'form': form, 'data':data, 'error_msg':e})
                
        
            # This section builds the data to return to the template as a list of 'JSON' style/dicts objects
            """
            E.g. something like
            data = [{'year':1998, 'month_list':[{'month':'January', 'total':2.89}]}, 
                    {'year':2005, 'month_list':[{'month':'October', 'total':53.99}]}, 
                    {'year':2010, 'month_list':[{'month':'March', 'total':3.99}]}]
            """
            
            # hit the database once
            query_set = ExpenseItem.objects.all()
            
            # get all distinct years
            years = query_set.dates('date','year')
            
            # option to sort years ASC or DESC...
            
            # Group by year
            for year in years:
                year_dict = {}
                
                year_dict['year'] = year.year
                
                month_list = []
                
                # Get the months for this year
                months = query_set.filter(date__year=year.year).dates('date','month')
                for month in months:
                    
                    month_dict = {}
                    
                    # build each month dict
                    month_dict['month'] = calendar.month_name[month.month]
                    result = query_set.filter(date__year=year.year).filter(date__month=month.month).aggregate(total_expenses_amount=Sum(F('total_amount'), output_field=FloatField()))
                    
                    month_dict['total'] = '%0.2f' % (result['total_expenses_amount']/100) # divide by 100 -> dollar and cents format
                    
                    # then add month dict to month list
                    month_list.append(month_dict)
                    
                year_dict['month_list'] = month_list
                 
                data.append(year_dict)   
    else:
        form = UploadFileForm()
        
    return render(request, 'upload.html', {'form': form, 'data':data, 'error_msg':None})
