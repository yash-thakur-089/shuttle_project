import django_tables2 as tables
from .models import Transaction
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class TransactionTable(tables.Table):
    timestamp = tables.Column(verbose_name='Date/Time')
    transaction_type = tables.Column(verbose_name='Type')
    amount = tables.Column(verbose_name='Amount')
    description = tables.Column(verbose_name='Description')
    remaining_balance = tables.Column(verbose_name='Balance')
    
    def render_timestamp(self, value):
        return value.strftime('%b %d, %Y %H:%M')
    
    def render_transaction_type(self, value):
        color = 'success' if value == 'CREDIT' else 'danger'
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            'Credit' if value == 'CREDIT' else 'Debit'
        )
    
    def render_amount(self, value):
        return mark_safe(f'${value:.2f}')
    
    def render_remaining_balance(self, value):
        return mark_safe(f'${value:.2f}')
    
    class Meta:
        model = Transaction
        template_name = 'django_tables2/bootstrap5.html'
        fields = ('timestamp', 'transaction_type', 'amount', 'description', 'remaining_balance')
        attrs = {
            'class': 'table table-striped table-hover',
        }