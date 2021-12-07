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


class PdCredential(models.Model):
    id = models.IntegerField(primary_key=True)
    credentialcode = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'pd_credential'

    def __str__(self):
        return self.credentialcode


class PdPrescriber(models.Model):
    npi = models.BigIntegerField(primary_key=True)
    fname = models.CharField(max_length=11)
    lname = models.CharField(max_length=11)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    state = models.ForeignKey(
        PdStatedata,
        on_delete=models.CASCADE,
        to_field='stateabbrev',
        db_column='state'
    )
    credentials = models.ManyToManyField(PdCredential, through='PdPrescriberCredential')
    specialty = models.CharField(max_length=62)
    isopioidprescriber = models.CharField(max_length=5, choices=[('TRUE', 'TRUE'), ('FALSE', 'FALSE')])
    totalprescriptions = models.IntegerField()
    drugs = models.ManyToManyField(PdDrugs, through='PdTriple')

    class Meta:
        # managed = False
        db_table = 'pd_prescriber'
    
    @classmethod
    def create(self, form):
        state = PdStatedata.objects.get(stateabbrev=form['state'])
        person = self(
            npi = form['npi'],
            fname = form['fname'].title(),
            lname = form['lname'].title(),
            gender = form['gender'],
            state = state,
            specialty = form['specialty'],
            isopioidprescriber = form['isopioidprescriber'],
            totalprescriptions = 0
        )
        
        return person

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

    @classmethod
    def create(self, tid, person, form):
        drug = PdDrugs.objects.get(drugname=form['drugname'])
        triple = self(
            id = tid,
            prescriberid = person,
            drugname = drug,
            qty = form['qty']
        )
        return triple

    def __str__(self):
        return f'{self.prescriberid}: {self.drugname}'

class PdPrescriberCredential(models.Model):
    id = models.IntegerField(primary_key=True)
    prescriberid = models.ForeignKey(
        'PdPrescriber', 
        on_delete=models.CASCADE,
        to_field='npi',
        db_column='prescriberid'
        )
    credential = models.ForeignKey(
        'PdCredential',
        on_delete=models.CASCADE,
        to_field='credentialcode',
        db_column='credential'
    )

    class Meta:
        # managed = False
        db_table = 'pd_prescriber_credential'

    @classmethod
    def create(self, id, person, form):
        c = PdCredential.objects.get(credentialcode=form['cred'])
        new = self(
            id = id,
            prescriberid = person,
            credential = c
        )
        return new

    
    def __str__(self):
        return f'{self.prescriberid} {self.credential}'
