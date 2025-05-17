from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Card
from .forms import CardForm
from django.views.generic import CreateView, ListView, UpdateView, DeleteView


class CardCreateView(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'vault/card_form.html'
    success_url = reverse_lazy('card-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CardListView(ListView):
    model = Card
    template_name = 'vault/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardUpdateView(UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'vault/card_form.html'
    success_url = reverse_lazy('card-list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardDeleteView(DeleteView):
    model = Card
    template_name = 'vault/card_delete.html'
    success_url = reverse_lazy('card_list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


