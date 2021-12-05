# from django.db import models

# class Prescriber(models.Model):
#     npi = models.IntegerField(primary_key=True, db_column='npi')
#     first_name = models.CharField(max_length=30, db_column='fname')
#     last_name = models.CharField(max_length=30, db_column='lname')
#     gender = models.CharField(
#         max_length=1, 
#         db_column='gender', 
#         verbose_name='gender',
#         choices=[('M', 'Male'), ('F', 'Female')]
#         )
#     state = models.CharField(max_length=2, verbose_name='state abbreviation')
#     credential = models.CharField(max_length=2, verbose_name='credential')
#     specialty = models.CharField(max_length=50, verbose_name='specialty')
#     is_opioid_prescriber = models.BooleanField(
#         db_column='isopioidprescriber', 
#         verbose_name='is opioid prescriber')
#     total_prescriptions = models.IntegerField(
#         db_column='totalprescriptions',
#         verbose_name='total prescriptions')
#     class Meta():
#         db_table = 'pd_prescriber'

#     def __str__(self):
#         return f'{self.first_name} {self.last_name}'

# class Drug(models.Model):
#     drugid = models.IntegerField(db_column='drugid', primary_key=True)
#     drug_name = models.CharField(
#         max_length=30, 
#         db_column='drugname', 
#         verbose_name='drug name')
#     is_opioid = models.CharField(
#         max_length=5, 
#         db_column='isopioid',
#         verbose_name='is opioid')
    
#     class Meta():
#         db_table = 'pd_drugs'
    
#     def __str__(self):
#         return self.drug_name

# class State(models.Model):
#     state_abbrev = models.CharField(
#         max_length=2,
#         db_column='stateabbrev',
#         verbose_name='state abbreviation',
#         primary_key=True)
#     state = models.CharField(
#         max_length=14,
#         db_column='state',
#         verbose_name='state name'
#         )
#     population = models.IntegerField()
#     death = models.IntegerField(
#         verbose_name='State Death Total'
#     )

#     class Meta():
#         db_table = 'pd_statedata'
    
#     def __str__(self):
#         return self.state
    
# class Triple(models.Model):
#     prescriber = models.ForeignKey(
#         Prescriber, 
#         verbose_name='prescriberID', 
#         on_delete=models.DO_NOTHING, 
#         to_field='npi')
#     drug_name = models.ForeignKey(
#         Drug,
#         verbose_name='drug name', 
#         on_delete=models.DO_NOTHING, 
#         to_field='drugid'
#         )
#     qty = models.IntegerField()

#     class Meta():
#         db_table = 'pd_triple'

#     def __str__(self):
#         return f'{self.prescriber}: {self.drug_name}'