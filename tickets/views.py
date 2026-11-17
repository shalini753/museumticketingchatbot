from django.shortcuts import render
from .models import TicketType


def home(request):
    tickets = TicketType.objects.filter(available=True)

    return render(
        request,
        'tickets/home.html',
        {'tickets': tickets}
    )