from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.db.models import Sum
from django.urls import reverse
from django_tables2 import RequestConfig
from .models import User, StudentProfile, Wallet, Transaction, AdminCreditAssignment
from .forms import StudentRegistrationForm, AdminCreditAssignmentForm
from .tables import TransactionTable




def home(request):
    return render(request, 'shuttle/home.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_student:
                return redirect('student_dashboard')
            elif user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    
    # GET request - show login form
    return render(request, 'shuttle/registration/login.html', {'form': AuthenticationForm()})


def custom_logout(request):
    logout(request)
    return redirect('home')

def student_check(user):
    return user.is_authenticated and user.is_student

def admin_check(user):
    return user.is_authenticated and user.is_admin

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email
            subject = 'Welcome to CGC Shuttle Management System'
            html_message = render_to_string('shuttle/email/welcome_email.html', {
                'user': user,
                'login_url': request.build_absolute_uri(reverse('login'))
            })
            plain_message = strip_tags(html_message)
            from_email = 'shuttle@cgc.edu'
            to = user.email
            
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            
            messages.success(request, 'Registration successful! Please check your email for login instructions.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'shuttle/registration/register.html', {'form': form})

@login_required
@user_passes_test(student_check, login_url='login')
def student_dashboard(request):
    wallet = Wallet.objects.get(student=request.user)
    recent_transactions = Transaction.objects.filter(wallet=wallet).order_by('-timestamp')[:5]
    
    context = {
        'wallet': wallet,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'shuttle/dashboard/student_dashboard.html', context)

@login_required
@user_passes_test(student_check, login_url='login')
def wallet_view(request):
    wallet = Wallet.objects.get(student=request.user)
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-timestamp')
    
    table = TransactionTable(transactions)
    RequestConfig(request, paginate={'per_page': 10}).configure(table)
    
    context = {
        'wallet': wallet,
        'transaction_table': table,
    }
    return render(request, 'shuttle/wallet/wallet.html', context)

@login_required
@user_passes_test(admin_check, login_url='login')
def admin_dashboard(request):
    total_students = User.objects.filter(is_student=True).count()
    total_credits_assigned = AdminCreditAssignment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    recent_assignments = AdminCreditAssignment.objects.select_related('student').order_by('-timestamp')[:5]
    
    context = {
        'total_students': total_students,
        'total_credits_assigned': total_credits_assigned,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'shuttle/dashboard/admin_dashboard.html', context)

@login_required
@user_passes_test(admin_check, login_url='login')
def assign_credits(request):
    if request.method == 'POST':
        form = AdminCreditAssignmentForm(request.POST, admin=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.admin = request.user
            
            # Get or create student's wallet
            student_wallet, created = Wallet.objects.get_or_create(
                student=assignment.student,
                defaults={'balance': 0}
            )
            
            # Update balance
            student_wallet.balance += assignment.amount
            student_wallet.save()
            
            # Create transaction record
            Transaction.objects.create(
                wallet=student_wallet,
                amount=assignment.amount,
                transaction_type='CREDIT',
                description=f"Admin credit: {assignment.reason}",
                remaining_balance=student_wallet.balance
            )
            
            assignment.save()
            
            # Send notification to student
            subject = 'Travel Credits Added to Your Account'
            html_message = render_to_string('shuttle/email/credit_assigned.html', {
                'student': assignment.student,
                'amount': assignment.amount,
                'reason': assignment.reason,
                'balance': student_wallet.balance,
                'login_url': request.build_absolute_uri(reverse('login'))
            })
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                'shuttle@cgc.edu',
                [assignment.student.email],
                html_message=html_message
            )
            
            messages.success(request, f'Successfully credited {assignment.amount} points to {assignment.student.username}')
            return redirect('admin_dashboard')
    else:
        form = AdminCreditAssignmentForm(admin=request.user)
    
    students = User.objects.filter(is_student=True).select_related('studentprofile')
    recent_assignments = AdminCreditAssignment.objects.select_related('student').order_by('-timestamp')[:5]
    
    return render(request, 'shuttle/admin/assign_credits.html', {
        'form': form,
        'students': students,
        'recent_assignments': recent_assignments
    })