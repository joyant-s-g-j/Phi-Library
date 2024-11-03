from django.shortcuts import render, redirect
from .forms import CategoryForm
# Create your views here.

def add_category(request):
    if request.method == "POST":
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect('add_category')
    else:
        category_form = CategoryForm()
    return render(request, 'add_category.html', {'form' : category_form})


