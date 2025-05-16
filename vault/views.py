from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Card
from .forms import CardForm
from django.views.generic import CreateView, ListView


class CardCreateView(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'vault/card_form.html'
    success_url = reverse_lazy('card-create')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CardListView(ListView):
    model = Card
    template_name = 'vault/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)




