from django.contrib import admin
from .models import TicketType, Booking


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available')
    search_fields = ('name',)
    list_filter = ('available',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'visitor_name',
        'ticket_type',
        'quantity',
        'visit_date',
        'total_amount',
        'status',
    )

    search_fields = ('visitor_name', 'visitor_email', 'booking_id')
    list_filter = ('status', 'visit_date')