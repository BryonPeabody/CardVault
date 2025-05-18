from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Card
from .forms import CardForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import fetch_card_data


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'vault/card_form.html'
    success_url = reverse_lazy('card-list')

    def form_valid(self, form):
        form.instance.user = self.request.user

        card_data = fetch_card_data(
            form.instance.name,
            form.instance.set_code
        )

        form.instance.image_url = card_data.get('image_url')
        print(card_data)
        return super().form_valid(form)


class CardListView(LoginRequiredMixin, ListView):
    model = Card
    template_name = 'vault/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'vault/card_form.html'
    success_url = reverse_lazy('card-list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardDeleteView(LoginRequiredMixin, DeleteView):
    model = Card
    template_name = 'vault/card_delete.html'
    success_url = reverse_lazy('card-list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "vault/register.html"
    success_url = reverse_lazy('login')
