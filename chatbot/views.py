import re
from datetime import date
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from tickets.models import TicketType, Booking


def chatbot_page(request):
    return render(request, 'chatbot/chat.html')


@require_POST
def chatbot_message(request):
    message = request.POST.get('message', '').strip()

    if not message:
        return JsonResponse({
            'reply': 'Please enter a response.'
        }, status=400)

    step = request.session.get('booking_step', 'start')

    if step == 'start':
        request.session['booking_data'] = {}
        request.session['booking_step'] = 'name'

        return JsonResponse({
            'reply': 'Welcome to Museum Explorer! What is your full name?'
        })

    data = request.session.get('booking_data', {})

    if step == 'name':
        if len(message) < 2:
            return JsonResponse({
                'reply': 'Please enter a valid name.'
            })

        data['name'] = message
        request.session['booking_step'] = 'email'

        reply = 'Please enter your email address.'

    elif step == 'email':
        if not re.fullmatch(
            r'[^@\s]+@[^@\s]+\.[^@\s]+',
            message
        ):
            return JsonResponse({
                'reply': 'That email address looks invalid. Please try again.'
            })

        data['email'] = message
        request.session['booking_step'] = 'ticket'

        tickets = TicketType.objects.filter(available=True)

        if not tickets.exists():
            return JsonResponse({
                'reply': 'Sorry, no tickets are available right now.'
            })

        options = '\n'.join(
            f"{ticket.pk}. {ticket.name} - ₹{ticket.price}"
            for ticket in tickets
        )

        reply = (
            'Which ticket would you like? Enter its number:\n'
            + options
        )

    elif step == 'ticket':
        if not message.isdigit():
            return JsonResponse({
                'reply': 'Please enter the number of a ticket from the list.'
            })

        ticket = TicketType.objects.filter(
            pk=int(message),
            available=True
        ).first()

        if ticket is None:
            return JsonResponse({
                'reply': 'That ticket is unavailable. Please choose a valid ticket number.'
            })

        data['ticket_id'] = ticket.pk
        request.session['booking_step'] = 'date'

        reply = (
            'Enter your visit date in YYYY-MM-DD format. '
            'For example, 2026-11-15.'
        )

    elif step == 'date':
        try:
            visit_date = date.fromisoformat(message)
        except ValueError:
            return JsonResponse({
                'reply': 'Invalid date. Please use YYYY-MM-DD.'
            })

        if visit_date < date.today():
            return JsonResponse({
                'reply': 'Please choose today or a future date.'
            })

        data['visit_date'] = message
        request.session['booking_step'] = 'quantity'

        reply = 'How many tickets would you like? Enter a number from 1 to 10.'

    elif step == 'quantity':
        if not message.isdigit() or not 1 <= int(message) <= 10:
            return JsonResponse({
                'reply': 'Please enter a quantity between 1 and 10.'
            })

        quantity = int(message)

        ticket = TicketType.objects.filter(
            pk=data['ticket_id'],
            available=True
        ).first()

        if ticket is None:
            return JsonResponse({
                'reply': 'This ticket is no longer available. Please start again.'
            })

        total = ticket.price * Decimal(quantity)

        booking = Booking.objects.create(
            visitor_name=data['name'],
            visitor_email=data['email'],
            ticket_type=ticket,
            quantity=quantity,
            visit_date=date.fromisoformat(data['visit_date']),
            total_amount=total,
            status='PENDING'
        )

        request.session['booking_step'] = 'start'
        request.session['booking_data'] = {}

        return JsonResponse({
            'reply': (
                'Your booking request has been saved!\n'
                f'Booking ID: {booking.booking_id}\n'
                f'Ticket: {ticket.name}\n'
                f'Quantity: {quantity}\n'
                f'Visit date: {booking.visit_date}\n'
                f'Total: ₹{booking.total_amount}\n'
                'Status: Pending payment.\n\n'
                'Payment has not been processed yet.'
            )
        })

    else:
        request.session['booking_step'] = 'start'
        request.session['booking_data'] = {}

        return JsonResponse({
            'reply': 'Let us start again. Send any message to begin.'
        })

    request.session['booking_data'] = data
    request.session.modified = True

    return JsonResponse({'reply': reply})