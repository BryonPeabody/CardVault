from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Card
from .forms import CardForm, CardUpdateForm
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from decimal import Decimal
from vault.services.image_services import get_card_image_url_or_placeholder
from vault.services.price_services import refresh_prices_for_user, create_initial_snapshot


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = "vault/card_form.html"
    success_url = reverse_lazy("card-list")

    def form_valid(self, form):
        form.instance.user = self.request.user

        form.instance.image_url = get_card_image_url_or_placeholder(
            card_name=form.instance.card_name,
            set_name=form.instance.set_name,
            card_number=form.instance.card_number,
        )

        parsed = getattr(form, "cleaned_price", None)
        if parsed and "price" in parsed:
            form.instance.value_usd = parsed["price"]
            form.instance.price_last_updated = parsed["price_date"]

        response = super().form_valid(form)
        create_initial_snapshot(self.object)
        return response


class CardListView(LoginRequiredMixin, ListView):
    model = Card
    template_name = "vault/card_list.html"
    context_object_name = "cards"

    def get_queryset(self):
        qs = Card.objects.filter(user=self.request.user)

        sort = self.request.GET.get("sort", "value_desc")

        if sort == "value_asc":
            return qs.order_by("value_usd", "card_name")
        elif sort == "value_desc":
            return qs.order_by("-value_usd", "card_name")
        elif sort == "set_asc":
            return qs.order_by("set_name", "card_number")
        elif sort == "set_desc":
            return qs.order_by("-set_name", "card_number")
        else:
            return qs.order_by("-value_usd", "card_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["current_sort"] = self.request.GET.get("sort", "value_desc")

        # Total value across the user's entire collection
        user_cards = Card.objects.filter(user=self.request.user)
        aggregates = user_cards.aggregate(
            total=Coalesce(Sum("value_usd"), Decimal("0"))
        )

        context["total_value_usd"] = aggregates["total"]

        return context


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    form_class = CardUpdateForm
    template_name = "vault/card_form.html"
    success_url = reverse_lazy("card-list")

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
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


@login_required
def refresh_prices(request):
    if request.method == "POST":
        refresh_prices_for_user(request.user)
    return redirect("card-list")


# ----------------------------------test helper


def health_check(request):
    return HttpResponse("OK", status=200)
