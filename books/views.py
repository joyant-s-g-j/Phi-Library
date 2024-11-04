from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, FormView
from django.urls import reverse_lazy
from .forms import ReviewForm, BookForm, DepositForm
from . models import Book, Order
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from datetime import datetime

def send_deposit_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount,
    })
    send_email = EmailMultiAlternatives(subject, message, to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

def send_purchased_email(user, book_name, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'book_name' : book_name,
    })
    send_email = EmailMultiAlternatives(subject, message, to=[user.email])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()

@method_decorator(login_required, name='dispatch')
class AddBookCreateView(UserPassesTestMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'add_book.html'
    success_url = reverse_lazy('basepage')

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('basepage')
    
@method_decorator(login_required, name='dispatch')
class EditBookView(UserPassesTestMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'edit_book.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('basepage')

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('basepage')
    
@method_decorator(login_required, name='dispatch')
class DeleteBookView(UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'delete.html'
    success_url = reverse_lazy('basepage')
    pk_url_kwarg = 'id'

    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('basepage')
    
@login_required
def book_buy(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        if request.method == 'POST':
            if book.quantity > 0:
                account = request.user.account
                if account.balance < book.book_price:
                    messages.error(request, 'Please deposit money to borrow books.')
                    return redirect('basepage')
                
                returned_order = Order.objects.filter(buyer=request.user, book=book, returned=True).first()
                
                if returned_order:
                    returned_order.returned = False
                    returned_order.save()
                
                account.balance -= book.book_price
                balance_after_order = account.balance
                account.save()

                amount = book.book_price 
                Order.objects.create(buyer=request.user, book=book, amount=amount, balance_after_order=balance_after_order)

                book.quantity -= 1
                book.buyer = request.user
                book.save()

                messages.success(request, f'You have successfully purchased {book.book_name}.')
                send_purchased_email(book.buyer, book.book_name, "Purchased Message", "purchased_email.html")
                return redirect('profile')
            else:
                messages.error(request, 'Sorry, this book is out of stock.')
                return redirect('basepage')
    except Book.DoesNotExist:
        messages.error(request, 'The book you are trying to purchase does not exist.')
        return redirect('profile')
    return render(request, 'book_buy.html', {'book': book})

@login_required
def order(request):
    order = Order.objects.filter(buyer = request.user)
    return render(request, 'profile.html', {'orders' : order})

class DetailBookView(DetailView):
    model = Book
    template_name = 'book_details.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            messages.error(request, 'You need to be logged in to leave a review.')
            return redirect('login')

        has_purchased = Order.objects.filter(buyer=request.user, book=self.object).exists()
        
        if not has_purchased:
            messages.error(request, 'You need to purchase this book to leave a review.')
            return redirect('detail_book', pk=self.object.pk)

        review_form = ReviewForm(data=request.POST)

        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.book = self.object
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Thank you for your review!')
        return redirect('detail_book', pk=self.object.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        reviews = book.review.all()
        
        review_form = ReviewForm()
        has_purchased = False
        has_returned = False

        if self.request.user.is_authenticated:
            has_purchased = Order.objects.filter(buyer=self.request.user, book=book).exists()
            has_returned = Order.objects.filter(buyer=self.request.user, book=book, returned=True).exists()

        context['reviews'] = reviews
        context['review_form'] = review_form
        context['can_review'] = has_purchased
        context['ratings'] = range(1, 6)
        context['has_purchased'] = has_purchased
        context['has_returned'] = has_returned
        return context

class DepositMoneyView(FormView):
    template_name = 'deposit.html'
    form_class = DepositForm
    success_url = reverse_lazy('basepage')  

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(update_fields=['balance'])
        
        messages.success(self.request, f'{amount} BDT was deposited to your account successfully.')
        send_deposit_email(self.request.user, amount, "Deposit Message", "deposit_email.html")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your submission.')
        return super().form_invalid(form)
    
class OrderReportView(LoginRequiredMixin, ListView):
    template_name = "order_report.html"
    model = Order
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = super().get_queryset().filter(buyer=self.request.user)

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

                queryset = queryset.filter(
                    timestamp__date__gte=start_date,
                    timestamp__date__lte=end_date
                )
            except ValueError:
                pass

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        account = getattr(self.request.user, 'account', None)
        
        if account:
            context['account'] = account
            context['balance'] = account.balance
        else:
            context['account'] = None
            context['balance'] = None

        return context

@login_required
def return_book(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    book = order.book

    # Update account balance and book quantity
    account = request.user.account
    account.balance += order.amount
    account.save()

    book.quantity += 1
    order.returned = True
    order.save()
    book.save()

    messages.success(request, f'You have successfully returned {book.book_name}.')
    return redirect('basepage')