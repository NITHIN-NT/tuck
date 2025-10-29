from django.shortcuts import render
from django.views.generic import TemplateView,DetailView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

# Create your views here.

class ProfileView(LoginRequiredMixin,TemplateView):
    template_name = 'userprofile/profile.html'
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user'] = self.request.user
        return context