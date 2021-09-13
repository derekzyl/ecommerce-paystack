from django.contrib import admin

# Register your models here.
from .models import Item, OrderItem, Order, Payment, Coupon, Payments


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']
admin.site.register(Item)
admin.site.register(OrderItem, OrderAdmin)
admin.site.register(Order),
admin.site.register(Payment),
admin.site.register(Payments),

admin.site.register(Coupon)
