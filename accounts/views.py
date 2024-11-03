from django.shortcuts import render, redirect
from .forms import RegistrationForm, ChangeUserForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.contrib.auth import login, logout
from django.views import View
from django.contrib import messages
# Create your views here.
     
class UserRegistrationView(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Registration successfully completed")
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'login.html'
    def get_success_url(self):
        return reverse_lazy('profile')
    
class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('basepage')
    
class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request):
        form = ChangeUserForm(instance=request.user)
        return render(request, self.template_name, {'form' : form})
    
    def post(self, request):
        form = ChangeUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form' : form})