import secrets

from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear')
)

LABEL_CHOICES = (
    ('p', 'primary'),
    ('s', 'secondary'),
    ('d', 'danger')
)

subCategory= (
    ('z', 'zara'),
    ('a', 'armani'),
    ('g', 'geogio')
)


class Item(models.Model):
    image = models.ImageField(default='default.jpg', upload_to='_photos')
    image2 = models.ImageField(default='default.jpg', upload_to='_photos')
    image3 = models.ImageField(default='default.jpg', upload_to='_photos')
    image4 = models.ImageField(default='default.jpg', upload_to='_photos')
    discountedPriced = models.FloatField(null=True, blank=True, default=None)

    title = models.CharField(max_length=100)
    price = models.FloatField()
    category = models.CharField(choices=CATEGORY_CHOICES, default='S', max_length=2 )
    label = models.CharField(choices=LABEL_CHOICES, default='p', max_length=1)
    subcategory = models.CharField(choices=subCategory, default= 'z', max_length= 1)
    itemName = models.CharField(max_length=100, default= '')
    slug = models.SlugField()

    description = models.CharField(max_length=50, default='')
    additionalInfo = models.CharField(max_length=50, default= '')



    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product', kwargs={
            'slug' : self.slug
        })
    def get_add_to_cart_url(self):
        return reverse('core:add_to_cart', kwargs={
            'slug' : self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse('core:remove_from_cart', kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete =models.CASCADE)
    quantity = models.IntegerField(default= 1)
    ordered= models.BooleanField(default=False)



    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
      return self.quantity * self.item.price




    def get_total_discount_item_price(self):
      return self.quantity * self.item.discountedPriced

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def final_item_price(self):
        if self.item.discountedPriced:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered= models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    billing_address = models.ForeignKey('BIllingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_final_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.final_item_price()
        return total


class BIllingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country =CountryField(multiple=False)
    state= models.CharField(max_length=100)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    charge_id = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code = models.CharField(max_length=15)

    def __str__(self):
        return self.code


class Payments(models.Model) :
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amo = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    ref = models.CharField(max_length=100)

    verified = models.BooleanField(default= False)
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self) -> str:
        return self.user.username

    def save(self, *args, **kwargs):
         while not self.ref:
             ref = secrets.token_urlsafe(50)
             object_with_similar_ref = Payments.objects.filter(ref=ref)
             if not object_with_similar_ref:
                 self.ref = ref
         super().save(*args,**kwargs)

    def amount(self):
       return self.amo.get_final_price()


    def amount_value(self) -> int:
        return self.amount * 100

    def email(self):
        return self.user.email