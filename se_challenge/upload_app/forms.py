from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Upload a file')

"""
A better approach is to validate the incoming data with a Django Form like so:
import csv
import StringIO
from django import forms
from .models import Purchase, Seller

class PurchaseForm(forms.ModelForm):
    class Meta:
    model = Purchase
    
def clean_seller(self):
    seller = self.cleaned_data["seller"]
    try:
        Seller.objects.get(name=seller)
    except Seller.DoesNotExist:
        msg = "{0} does not exist in purchase #{1}.".format(
        seller,
        self.cleaned_data["purchase_number"])

        raise forms.ValidationError(msg)
    return seller
def add_csv_purchases(rows):
    rows = StringIO.StringIO(rows)

    records_added = 0
    errors = []
    # Generate a dict per row, with the first CSV row being the keys.
    for row in csv.DictReader(rows, delimiter=","):
        # Bind the row data to the PurchaseForm.
        form = PurchaseForm(row)

        # Check to see if the row data is valid.
        if form.is_valid():
            # Row data is valid so save the record.
            form.save()
            records_added += 1
        else:
            errors.append(form.errors)
    
    return records_added, errors
"""
