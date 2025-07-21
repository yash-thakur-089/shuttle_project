from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    university_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.username} ({self.university_id})"

class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='student_profile'
    )
    department = models.CharField(max_length=100)
    semester = models.PositiveIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department} Sem {self.semester}"

class Wallet(models.Model):
    student = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_student': True},
        related_name='student_wallet'
    )
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)]
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username}'s Wallet - ${self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]
    
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.transaction_type} of ${self.amount} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class AdminCreditAssignment(models.Model):
    admin = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'is_admin': True},
        related_name='admin_credits_assigned'
    )
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_student': True},
        related_name='student_credits_received'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Admin Credit Assignment'
        verbose_name_plural = 'Admin Credit Assignments'
        ordering = ['-timestamp']
    
    def __str__(self):
        admin_name = self.admin.username if self.admin else 'System'
        return f"Credit of ${self.amount} to {self.student.username} by {admin_name}"