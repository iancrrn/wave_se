# Ian Carreon, iancrrn@gmail.com
# September 28, 2016

# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

# Another useful benefit of F() is that having the database - rather than Python - update a field's value avoids a race condition.
# F() is also very useful in QuerySet filters, where they make it possible to filter a set of objects 
# against criteria based on their field values, rather than on Python values.
from django.db.models import F, FloatField, DecimalField, Sum
from django.db import connection, reset_queries

from .forms import UploadFileForm

from .models import *
#from .models import Employee
#from .models import ExpenseItem

import csv
import StringIO
from datetime import date
import calendar


def handle_uploaded_file(f):
    
    for chunk in f.chunks():        
        f = StringIO.StringIO(chunk)
        csvreader = csv.reader(f)
 
        # This skips the first row (i.e. header) of the CSV file.
        next(csvreader)

        for row in csvreader:
            # do stuff with each row...
        
            # remove any whitespace
            row = [i.strip() for i in row]
            
            # Extract the expense item part
            expense_date = row[0].split('/') # extract year, month, day
            year = int(expense_date[2])
            month = int(expense_date[0])
            day = int(expense_date[1])
            
            category = row[1]
            description = row[4]
            
            # Work with integers - avoid issues working with floats
            # Convert to cents (i.e. multiply by 100) use DecimalField
            pre_tax_amount = int(float(row[5].replace(',', '')) * 100)
            tax_name = row[6]
            tax_amount = int(float(row[7].replace(',', '')) * 100)
            total_amount = int(pre_tax_amount + tax_amount)
                    
            # Extract employee part
            employee_name = [i.strip() for i in row[2].split()]
            first_name = employee_name[0]
            last_name = employee_name[1]
            address = row[3]
            
            # To improve performance use bulk_create and transactions
            """
            try:
                with transaction.atomic():
                    # do your bulk insert / update operation
                    q = some list of employees
                    objs = [
                        Employees(
                            first_name=first_name,
                            first_name=first_name,
                            address=address,
                        )
                        for e in q
                    ]
                    msg = Employee.objects.bulk_create(objs)            
            except IntegrityError:
                pass
                # rollback...

            expense_item = ExpenseItem(yada=yada, ...)
            expense_item.employee_id = 5 # query then lookup using dict
            expense_item.save()                
            """
            
            # If employee already in the databaase then use that otherwise create a new entry
            employee, created = Employee.objects.get_or_create(first_name=first_name, last_name=last_name, address=address)

            # If this expense item is already assigned to this employee then do nothing else create a new expense item for this employee
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
            except Exception as e: 
                return render(request, 'upload.html', {'form': form, 'data':data, 'error_msg':e})
                
            # This section builds the data returned to the template as a list of 'JSON' style/dicts objects
            """
            E.g. something like
            data = [{'year':1998, 'month_list':[{'month':'January', 'total':2.89}]}, 
                    {'year':2005, 'month_list':[{'month':'October', 'total':53.99}]}, 
                    {'year':2010, 'month_list':[{'month':'March', 'total':3.99}]}]
            """
            
            query_set = ExpenseItem.objects.all()
            
            """
            query_set = ExpenseItem.objects.all().prefetch_related('employee') # 1            
            query_set = ExpenseItem.objects.select_related().all().values('tax_name') # 1
            query_set = ExpenseItem.objects.select_related().all().values_list('tax_name', flat=True).distinct() # 1
            query_set = ExpenseItem.objects.select_related().all()  # 1
            """
            
            """
            Most ORMs have lazy-loading enabled by default, so queries are issued for the parent record, 
            and then one query for EACH child record. As you can expect, 
            doing N+1 queries instead of a single query will flood your database with queries, 
            which is something we can and should avoid.
            E.g. the code below will result in n + 1 queries
            
            query_set = ExpenseItem.objects.all() 
            for i in query_set:
                print i.employee.id
                print i.tax_amount
            """
                
            print '1. Number of queries: ', len(connection.queries)
            #print query_set.query            

            print 'Queries: ', len(connection.queries)
            reset_queries()
            
            """
            "year" returns a list of all distinct year values for the field.
            "month" returns a list of all distinct year/month values for the field.
            "day" returns a list of all distinct year/month/day values for the field.
            """
            years = query_set.dates('date','year', order='DESC') # order='ASC' - default
            
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
                    #result = query_set.filter(date__year=year.year).filter(date__month=month.month).aggregate(total_expenses_amount=Sum(F('total_amount'), output_field=DecimalField()))
                    result = query_set.filter(date__year=year.year).filter(date__month=month.month).aggregate(total_expenses_amount=Sum(F('total_amount')))
                    
                    month_dict['total'] = '%0.2f' % (result['total_expenses_amount']/100) # divide by 100 -> dollar and cents format
                    
                    # then add this month dict to the month list
                    month_list.append(month_dict)
                    
                year_dict['month_list'] = month_list
                 
                data.append(year_dict)   
    else:
        form = UploadFileForm()
        
    return render(request, 'upload.html', {'form': form, 'data':data, 'error_msg':None})
    
    
    
# when using alternative models
                                    
"""
# Alternative
# Extract the expense item part
expense_date = row[0].split('/') # extract year, month, day
year = int(expense_date[2])
month = int(expense_date[0])
day = int(expense_date[1])

categories = row[1].split('and')

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
street_obj, created = Street.objects.get_or_create(street=street)

city = address[1].strip()
state_and_zipcode = address[2].strip()

temp = state_and_zipcode.split(' ')
state = temp[0].strip()
zipcode = temp[1].strip()

zipcode_obj, created = ZipCode.objects.get_or_create(zipcode=zipcode, city=city, state=state)
employee_obj, created = Employee.objects.get_or_create(first_name=first_name, last_name=last_name, street=street_obj, zipcode=zipcode_obj)
            
taxname_obj, created = TaxName.objects.get_or_create(tax_name=tax_name)

expense_obj, created = Expense.objects.get_or_create(date=date(year, month, day), description=description, 
                        pre_tax_amount=pre_tax_amount, tax_name=taxname_obj, tax_amount=tax_amount, total_amount=total_amount, employee=employee_obj)

# for each category
for category in categories:
    category_obj, created = Category.objects.get_or_create(name=category)
    expense_obj.categories.add(category_obj)            
"""
    
    
    
    
"""
To avoid this problem, simply save the QuerySet and reuse it:

>>> queryset = Entry.objects.all()
>>> print([p.headline for p in queryset]) # Evaluate the query set.
>>> print([p.pub_date for p in queryset]) # Re-use the cache from the evaluation.


When QuerySets are not cached

Querysets do not always cache their results. When evaluating only part of the queryset, the cache is checked, but if it is not populated then the items returned by the subsequent query are not cached. Specifically, this means that limiting the queryset using an array slice or an index will not populate the cache.

For example, repeatedly getting a certain index in a queryset object will query the database each time:

>>> queryset = Entry.objects.all()
>>> print queryset[5] # Queries the database
>>> print queryset[5] # Queries the database again
However, if the entire queryset has already been evaluated, the cache will be checked instead:

>>> queryset = Entry.objects.all()
>>> [entry for entry in queryset] # Queries the database
>>> print queryset[5] # Uses cache
>>> print queryset[5] # Uses cache
Here are some examples of other actions that will result in the entire queryset being evaluated and therefore populate the cache:

>>> [entry for entry in queryset]
>>> bool(queryset)
>>> entry in queryset
>>> list(queryset)

Complex lookups with Q objects

Keyword argument queries - in filter(), etc. - are 'AND'ed together. If you need to execute more complex queries (for example, queries with OR statements), you can use Q objects.

A Q object (django.db.models.Q) is an object used to encapsulate a collection of keyword arguments. These keyword arguments are specified as in 'Field lookups' above.

For example, this Q object encapsulates a single LIKE query:

from django.db.models import Q
Q(question__startswith='What')
Q objects can be combined using the & and | operators. When an operator is used on two Q objects, it yields a new Q object.

For example, this statement yields a single Q object that represents the 'OR' of two "question__startswith" queries:

Q(question__startswith='Who') | Q(question__startswith='What')
This is equivalent to the following SQL WHERE clause:

WHERE question LIKE 'Who%' OR question LIKE 'What%'
You can compose statements of arbitrary complexity by combining Q objects with the & and | operators and use parenthetical grouping. Also, Q objects can be negated using the ~ operator, allowing for combined lookups that combine both a normal query and a negated (NOT) query:

Q(question__startswith='Who') | ~Q(pub_date__year=2005)
Each lookup function that takes keyword-arguments (e.g. filter(), exclude(), get()) can also be passed one or more Q objects as positional (not-named) arguments. If you provide multiple Q object arguments to a lookup function, the arguments will be 'AND'ed together. For example:

Poll.objects.get(
    Q(question__startswith='Who'),
    Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6))
)
... roughly translates into the SQL:

SELECT * from polls WHERE question LIKE 'Who%'
    AND (pub_date = '2005-05-02' OR pub_date = '2005-05-06')

Lookup functions can mix the use of Q objects and keyword arguments. All arguments provided to a lookup function (be they keyword arguments or Q objects) are 'AND'ed together. However, if a Q object is provided, it must precede the definition of any keyword arguments. For example:

Poll.objects.get(
    Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6)),
    question__startswith='Who',
)

Following relationships 'backward'

If a model has a ForeignKey, instances of the foreign-key model will have access to a Manager that returns all instances of the first model. By default, this Manager is named FOO_set, where FOO is the source model name, lowercased. This Manager returns QuerySets, which can be filtered and manipulated as described in the 'Retrieving objects' section above.

Example:

>>> b = Blog.objects.get(id=1)
>>> b.entry_set.all() # Returns all Entry objects related to Blog.

# b.entry_set is a Manager that returns QuerySets.
>>> b.entry_set.filter(headline__contains='Lennon')
>>> b.entry_set.count()

# Total number of books.
>>> Book.objects.count()
2452

# Total number of books with publisher=BaloneyPress
>>> Book.objects.filter(publisher__name='BaloneyPress').count()
73

# Average price across all books.
>>> from django.db.models import Avg
>>> Book.objects.all().aggregate(Avg('price'))
{'price__avg': 34.35}

# Max price across all books.
>>> from django.db.models import Max
>>> Book.objects.all().aggregate(Max('price'))
{'price__max': Decimal('81.20')}

# Cost per page
>>> from django.db.models import F, FloatField, Sum
>>> Book.objects.all().aggregate(
...    price_per_page=Sum(F('price')/F('pages'), output_field=FloatField()))
{'price_per_page': 0.4470664529184653}

# All the following queries involve traversing the Book<->Publisher
# foreign key relationship backwards.

# Each publisher, each with a count of books as a "num_books" attribute.
>>> from django.db.models import Count
>>> pubs = Publisher.objects.annotate(num_books=Count('book'))
>>> pubs
<QuerySet [<Publisher: BaloneyPress>, <Publisher: SalamiPress>, ...]>
>>> pubs[0].num_books
73

# The top 5 publishers, in order by number of books.
>>> pubs = Publisher.objects.annotate(num_books=Count('book')).order_by('-num_books')[:5]
>>> pubs[0].num_books
1323


Generating aggregates for each item in a QuerySet

The second way to generate summary values is to generate an independent summary for each object in a QuerySet. For example, if you are retrieving a list of books, you may want to know how many authors contributed to each book. Each Book has a many-to-many relationship with the Author; we want to summarize this relationship for each book in the QuerySet.

Per-object summaries can be generated using the annotate() clause. When an annotate() clause is specified, each object in the QuerySet will be annotated with the specified values.

The syntax for these annotations is identical to that used for the aggregate() clause. Each argument to annotate() describes an aggregate that is to be calculated. For example, to annotate books with the number of authors:

# Build an annotated queryset
>>> from django.db.models import Count
>>> q = Book.objects.annotate(Count('authors'))
# Interrogate the first object in the queryset
>>> q[0]
<Book: The Definitive Guide to Django>
>>> q[0].authors__count
2
# Interrogate the second object in the queryset
>>> q[1]
<Book: Practical Django Projects>
>>> q[1].authors__count
1
As with aggregate(), the name for the annotation is automatically derived from the name of the aggregate function and the name of the field being aggregated. You can override this default name by providing an alias when you specify the annotation:

>>> q = Book.objects.annotate(num_authors=Count('authors'))
>>> q[0].num_authors
2
>>> q[1].num_authors
1
Unlike aggregate(), annotate() is not a terminal clause. The output of the annotate() clause is a QuerySet; this QuerySet can be modified using any other QuerySet operation, including filter(), order_by(), or even additional calls to annotate().

>>> from django.db.models import Count, Min, Sum, Avg
>>> Publisher.objects.annotate(Count('book'))
(Every Publisher in the resulting QuerySet will have an extra attribute called book__count.)


Aggregating annotations

You can also generate an aggregate on the result of an annotation. When you define an aggregate() clause, the aggregates you provide can reference any alias defined as part of an annotate() clause in the query.

For example, if you wanted to calculate the average number of authors per book you first annotate the set of books with the author count, then aggregate that author count, referencing the annotation field:

>>> from django.db.models import Count, Avg
>>> Book.objects.annotate(num_authors=Count('authors')).aggregate(Avg('num_authors'))
{'num_authors__avg': 1.66}
"""    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    








