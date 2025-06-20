from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Card
from .forms import CardForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import fetch_card_data, fetch_card_price, extract_card_price
from django.conf import settings
from django.http import JsonResponse
import requests


def test_card_price_view(request):
    api_data = fetch_card_price("Charizard V", "swsh3")
    parsed = extract_card_price(api_data, "Charizard V", "19", "swsh3")
    return JsonResponse(parsed)


def test_charizard_sv03(request):
    url = "https://www.pokemonpricetracker.com/api/v1/prices"
    headers = {"Authorization": f"Bearer {settings.CARDVAULT_API_KEY}"}
    params = {"setId": "sv3", "name": "Charizard ex"}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    print("DEBUG API RAW:", data)

    return JsonResponse(data)  # Just dump it back to browser


def test_get_all_sets(request):
    url = "https://www.pokemonpricetracker.com/api/v1/sets"
    headers = {"Authorization": f"Bearer {settings.CARDVAULT_API_KEY}"}

    response = requests.get(url, headers=headers)
    print("DEBUG SET RESPONSE:", response.json())
    return JsonResponse(response.json(), safe=False)


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = "vault/card_form.html"
    success_url = reverse_lazy("card-list")

    def form_valid(self, form):
        form.instance.user = self.request.user

        card_data = fetch_card_data(
            form.instance.name, form.instance.set_code, form.instance.card_number
        )

        form.instance.image_url = card_data.get("image_url")

        # debug: see what im sending
        print("sending name:", form.instance.name)
        print("sending set_code:", form.instance.set_code)
        print("sending card_number", form.instance.card_number)

        price_api_data = fetch_card_price(form.instance.name, form.instance.set_code)

        # debug: check api response
        # print("raw price api data:", price_api_data)
        print("data key present:", "data" in price_api_data)
        print("data length:", len(price_api_data.get("data", [])))

        parsed = extract_card_price(
            price_api_data,
            form.instance.name,
            form.instance.card_number,
            form.instance.set_code,
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
            name=form.cleaned_data.get("name"),
            set_code=form.cleaned_data.get("set_code"),
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
