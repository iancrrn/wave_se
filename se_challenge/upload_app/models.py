# Ian Carreon, iancrrn@gmail.com

from __future__ import unicode_literals

from django.db import models

# Create your models here.
    
class Employee(models.Model):
    
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.CharField(max_length=255)

    class Meta:
        unique_together = ("first_name", "last_name", "address")
                
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
    
    """
    This is the behaviour to adopt when the referenced object is deleted. It is not specific to django, this is an SQL standard.
    CASCADE: When the referenced object is deleted, also delete the objects that have references to it.
    When you remove an employee youmay want to remove the employee's expenses as well
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    
    # Ensure no duplicates
    class Meta:
        unique_together = ("date", "category", "description", "tax_name", "pre_tax_amount", "tax_amount", "total_amount", "employee")



"""
OneToOneField
A one-to-one relationship. Conceptually, this is similar to a ForeignKey with unique=True, 
but the "reverse" side of the relation will directly return a single object.
"""

# Alternative models    
"""
class Employee(models.Model):
    
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    street = models.ForeignKey('Street')
    zipcode = models.ForeignKey('ZipCode')
    #manager = models.ForeignKey('self')

    class Meta:
        unique_together = ("first_name", "last_name", "street")

class Street(models.Model):
    street = models.CharField(max_length=100, primary_key = True) # Make this the PK since streets with street numbers are unique
                
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
    
    # quantize result has too many digits for current context - error if not enough max_digits
    pre_tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    tax_name = models.ForeignKey(TaxName)
    categories = models.ManyToManyField(Category)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ("date", "id", "description", "pre_tax_amount", "employee")
    
class Hobby(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
"""


"""
# example of OneToOneField 
class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

    def __str__(self):  # __unicode__ on Python 2
        return "%s the place" % self.name

class Restaurant(models.Model):
    place = models.OneToOneField(
        Place,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    serves_hot_dogs = models.BooleanField(default=False)
    serves_pizza = models.BooleanField(default=False)

    def __str__(self):              # __unicode__ on Python 2
        return "%s the restaurant" % self.place.name
"""
