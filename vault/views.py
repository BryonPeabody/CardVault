from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Card
from .forms import CardForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import fetch_card_data, fetch_card_price, extract_card_price
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import requests


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = "vault/card_form.html"
    success_url = reverse_lazy("card-list")

    def form_valid(self, form):
        form.instance.user = self.request.user

        card_data = fetch_card_data(
            form.instance.card_name,
            form.instance.set_name,
            form.instance.card_number,
        )

        form.instance.image_url = card_data.get("image_url")

        # debug: see what im sending
        print("sending card_name:", form.instance.card_name)
        print("sending set_name:", form.instance.set_name)
        print("sending card_number", form.instance.card_number)
        price_api_data = fetch_card_price(
            form.instance.card_name, form.instance.set_name
        )
        # debug: check api response
        # print("raw price api data:", price_api_data)
        print("data key present:", "data" in price_api_data)
        print("data length:", len(price_api_data.get("data", [])))
        parsed = extract_card_price(
            price_api_data,
            form.instance.card_number,
        )
        if parsed and "price" in parsed:
            form.instance.value_usd = parsed["price"]
            form.instance.price_last_updated = parsed["price_date"]

        return super().form_valid(form)


class CardListView(LoginRequiredMixin, ListView):
    model = Card
    template_name = "vault/card_list.html"
    context_object_name = "cards"

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = "vault/card_form.html"
    success_url = reverse_lazy("card-list")

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user

        card_data = fetch_card_data(
            card_name=form.cleaned_data.get("card_name"),
            set_name=form.cleaned_data.get("set_name"),
            card_number=form.cleaned_data.get("card_number"),
        )

        if card_data:
            form.instance.image_url = card_data.get("image_url")

        return super().form_valid(form)


class CardDeleteView(LoginRequiredMixin, DeleteView):
    model = Card
    template_name = "vault/card_delete.html"
    success_url = reverse_lazy("card-list")

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "vault/register.html"
    success_url = reverse_lazy("login")


# ----------------------------------test helper


def health_check(request):
    return HttpResponse("OK", status=200)
