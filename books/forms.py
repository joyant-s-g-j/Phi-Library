from django import forms
from . models import Book, Review, Order

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['book_name', 'author', 'content', 'book_price', 'category', 'quantity', 'image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'body']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['amount']  

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.account = self.account  
        self.instance.balance_after_order = self.account.balance  
        return super().save(commit)

class DepositForm(OrderForm):
    def clean_amount(self):
        min_deposite_amount = 10
        amount = self.cleaned_data.get('amount')
        if amount < min_deposite_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposite_amount} BDT.'
            )
        return amount