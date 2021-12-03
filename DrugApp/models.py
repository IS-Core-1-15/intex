# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import math
from django import forms
from django.db import models

class PdStatedata(models.Model):
    state = models.CharField(max_length=14)
    stateabbrev = models.CharField(max_length=2, primary_key=True)
    population = models.IntegerField()
    deaths = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'pd_statedata'

    def __str__(self):
        return self.state

class PdDrugs(models.Model):
    drugid = models.IntegerField(primary_key=True)
    drugname = models.CharField(max_length=30, unique=True)
    isopioid = models.CharField(max_length=5)

    class Meta:
        # managed = False
        db_table = 'pd_drugs'
    
    def __str__(self):
        return self.drugname


class PdPrescriber(models.Model):
    npi = models.IntegerField(primary_key=True)
    fname = models.CharField(max_length=11)
    lname = models.CharField(max_length=11)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    state = models.ForeignKey(
        PdStatedata,
        on_delete=models.CASCADE,
        to_field='stateabbrev',
        db_column='state'
    )
    credentials1 = models.CharField(max_length=10, blank=True, null=True)
    credentials2 = models.CharField(max_length=10, blank=True, null=True)
    credentials3 = models.CharField(max_length=10, blank=True, null=True)
    credentials4 = models.CharField(max_length=10, blank=True, null=True)
    specialty = models.CharField(max_length=62)
    isopioidprescriber = models.CharField(max_length=5, choices=[('TRUE', 'TRUE'), ('FALSE', 'FALSE')])
    totalprescriptions = models.IntegerField()
    drugs = models.ManyToManyField(PdDrugs, through='PdTriple')
    class Meta:
        # managed = False
        db_table = 'pd_prescriber'

    def __str__(self):
        return f'{self.fname} {self.lname}'

class PdTriple(models.Model):
    id = models.IntegerField(primary_key=True)
    prescriberid = models.ForeignKey(
        'PdPrescriber', 
        on_delete=models.CASCADE,
        to_field='npi',
        db_column='prescriberid'
        )
    drugname = models.ForeignKey(
        'PdDrugs',
        on_delete=models.CASCADE,
        to_field='drugname',
        db_column='drugname'
        )
    qty = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'pd_triple'

    def __str__(self):
        return f'{self.prescriberid}: {self.drugname}'