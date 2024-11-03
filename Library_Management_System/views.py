from django.shortcuts import render, get_object_or_404
from books.models import Book
from categories.models import Category
def home(request, category_slug = None):
    data = Book.objects.all()
    if category_slug is not None:
        category = get_object_or_404(Category, slug = category_slug)
        data = Book.objects.filter(category = category)
    categories = Category.objects.all()
    return render(request, 'home.html', {'data' : data, 'categories' : categories})