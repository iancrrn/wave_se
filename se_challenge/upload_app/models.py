# Ian Carreon, iancrrn@gmail.com

from __future__ import unicode_literals

from django.db import models

# Create your models here.



class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    author = models.ForeignKey(Author, related_name='books')
    title = models.CharField(max_length=100)
        
    
# Option: have another model called EmployeeProfile to store address, and other info... 1 to 1 relationship with Employee model
class Employee(models.Model):
    
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.CharField(max_length=255)

    # we probably don't need this constraint if we had some unique field to identify each employee
    # such as an email address
    class Meta:
        unique_together = ("first_name", "last_name", "address") # add address since we can have 2 John Smiths living at different addresses
                

# Assumptions
# 1. One-to-Many relationship: One Employee Has Many Expense Items, an Expense Item is not reused between Employees
# 2. No duplicates of Expense Items

class ExpenseItem(models.Model):
    date = models.DateField()
    category = models.CharField(max_length=30)
    description = models.CharField(max_length=30)
    tax_name = models.CharField(max_length=30)
    
    # Note:
    # I decide to work with cents (integers) for the monetary values
    # I came across an issue with this row in the csv file
    # 12/14/2013,Computer - Software,Tim Cook,"1 Infinite Loop, Cupertino, CA 95014",Microsoft Office, 899.00 ,CA Sales tax, 67.43 
    # it would be duplicated in the database table if I used a FloatField with total_amount
    # i.e. total_amount = models.FloatField()
    
    pre_tax_amount = models.IntegerField()
    tax_amount = models.IntegerField()
    total_amount = models.IntegerField()
    
    employee = models.ForeignKey(Employee) #, on_delete=models.CASCADE)
    
    # Ensure no duplicates
    class Meta:
        unique_together = ("date", "category", "description", "tax_name", "pre_tax_amount", "tax_amount", "total_amount", "employee")
    

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
    #category = models.ForeignKey(Category)
    categories = models.ManyToManyField(Category)
    employee = models.ForeignKey(Employee) #, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ("date", "description", "pre_tax_amount", "employee")
    
class Hobby(models.Model):
    employee = models.ForeignKey(Employee) #, on_delete=models.CASCADE)
"""
