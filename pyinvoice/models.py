from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)

class Invoice(models.Model):
    number = models.CharField(max_length=100)
    total_gross =  models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now=True)
    company = models.ForeignKey(Company)
    seen = models.BooleanField()
    paid = models.BooleanField()
    

class Document(models.Model):
    invoice = models.ForeignKey(Invoice)
    title = models.CharField(max_length=100)
    document_file = models.FileField(upload_to='documents/%Y/%m/%d')
