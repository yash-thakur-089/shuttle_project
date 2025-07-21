from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Transaction, Wallet, StudentProfile, AdminCreditAssignment
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class CGCEmailValidator:
    def __call__(self, value):
        validate_email(value)
        if not value.endswith('@cgc.edu'):
            raise ValidationError('Only CGC university email addresses are allowed (@cgc.edu)')

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(validators=[CGCEmailValidator()])
    university_id = forms.CharField(max_length=20, label="University ID")
    phone = forms.CharField(max_length=15)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    department = forms.CharField(max_length=100)
    semester = forms.IntegerField(min_value=1, max_value=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'university_id', 'phone', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.university_id = self.cleaned_data['university_id']
        user.phone = self.cleaned_data['phone']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_student = True
        
        if commit:
            user.save()
            # Create student profile
            profile = StudentProfile(
                user=user,
                department=self.cleaned_data['department'],
                semester=self.cleaned_data['semester']
            )
            profile.save()
            
            # Create wallet with initial balance 0
            wallet = Wallet.objects.create(student=user, balance=0)
            
            # Create initial transaction
            Transaction.objects.create(
                wallet=wallet,
                amount=0,
                transaction_type='CREDIT',
                description="Initial wallet creation",
                remaining_balance=0
            )
        
        return user

class AdminCreditAssignmentForm(forms.ModelForm):
    class Meta:
        model = AdminCreditAssignment
        fields = ['student', 'amount', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        admin = kwargs.pop('admin', None)
        super().__init__(*args, **kwargs)
        if admin:
            self.fields['student'].queryset = User.objects.filter(is_student=True)