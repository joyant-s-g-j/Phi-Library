from django.urls import path
from .views import AddBookCreateView, EditBookView, DeleteBookView, DetailBookView, book_buy, OrderReportView, DepositMoneyView, return_book
urlpatterns = [
    path('add/', AddBookCreateView.as_view(), name='add_book'),
    path('edit/<int:id>/', EditBookView.as_view(), name='edit_book'),
    path('delete/<int:id>/', DeleteBookView.as_view(), name='delete_book'),
    path('details/<int:pk>/', DetailBookView.as_view(), name='detail_book'),
    path('buy/<int:book_id>/', book_buy, name='book_buy'),
    path('report/', OrderReportView.as_view(), name="order_report"),
    path('deposit/', DepositMoneyView.as_view(), name='deposit_money'),
    path('return/<int:order_id>/', return_book, name="book_return")
]
