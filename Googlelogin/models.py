from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
import os

def unique_short_file_name_photo(instance, filename):
    ext = filename.split('.')[-1]
    short_uuid = uuid.uuid4().hex[:8]
    return os.path.join("assets/", f"{short_uuid}.{ext}")

def unique_short_file_name_resume(instance, filename):
    ext = filename.split('.')[-1]
    short_uuid = uuid.uuid4().hex[:8]
    return os.path.join("resume/", f"{short_uuid}.{ext}")

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField( max_length=100,unique=True)
    phone = models.CharField( max_length=15)
    name = models.CharField( max_length=50)
    password = models.CharField(max_length=128)
    photo = models.ImageField(upload_to=unique_short_file_name_photo, blank=True, null=True)
    resume = models.FileField(upload_to=unique_short_file_name_resume, blank=True, null=True)
    workStatus = models.CharField(max_length=50, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'registration_for_jobportal'




class PostedJob(models.Model):
    company_name = models.CharField(max_length=200)
    employee_id= models.CharField(max_length=100)
    job_id = models.CharField(max_length=200, unique=True, editable=False)
    job_title = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    experience = models.CharField(max_length=200)
    salary = models.CharField(max_length=200)
    work_mode = models.CharField(max_length=200)
    education = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.job_id:
            self.job_id = str(uuid.uuid4()).replace('-', '')[:12]
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'Posted_jobs'



class Save_post_By_user(models.Model):
    user=models.ForeignKey(CustomUser,max_length=100,on_delete=models.DO_NOTHING)
    job_id = models.CharField(max_length=200, editable=True)
    job_title = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    experience = models.CharField(max_length=200)
    salary = models.CharField(max_length=200)
    work_mode = models.CharField(max_length=200)
    education = models.CharField(max_length=200)
    company_name=models.CharField(max_length=200)


        
    class Meta:
        db_table = 'Save_post_by_user'
        
        
        
# models.py

from django.db import models

class Plan1(models.Model):
    plan_id = models.CharField(max_length=100)
    plain_discreption = models.CharField(max_length=200)
    post = models.IntegerField()

    def __str__(self):
        return self.plan_id
    
    class Meta:
        db_table = 'Plan1'


class FinalSubscriptionForEmployee(models.Model):
    plan = models.ForeignKey(Plan1, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=100)
    receipent_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} → {self.receipent_id}"
    
    class Meta:
        db_table = 'Final_subscrtion_for_employee'
