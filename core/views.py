import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View

from .forms import CheckoutForm
from .models import Item, OrderItem, Order, BIllingAddress, Payment, Coupon, Payments

from pypaystack  import Transaction, Customer, Plan
# Create your views here.

def products(request):
    context = {
        'items' : Item.objects.all()
    }
    return render( request, 'product.html', context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context= {
            'form' : form
        }
        return render(self.request, 'checkout.html', context)
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered =False)
            if form.is_valid():
                street_address = form.cleaned_data.get(
                    'street_address'
                )
                apartment_address = form.cleaned_data.get(
                    'apartment_address'
                )
                country = form.cleaned_data.get(
                    'country'
                )
                state = form.cleaned_data.get(
                    'state'
                )
                zip = form.cleaned_data.get(
                    'zip'
                )
                # TODO: add functionality to these field
                # same_shipping_address = form.cleaned_data.get(
                #     'same_billing_address'
                # )
                # save_info = form.cleaned_data.get(
                #     'save_info'
                # )

                payment_option = form.cleaned_data.get(
                    'payment_option'

                )
                billing_address = BIllingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    state = state,
                    zip=zip

                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                #TODO add routing to payment option
                messages.info(self.request, 'form is valid')

                return redirect('core:payment')
        except ObjectDoesNotExist:
            messages.error(self.request, "you dont have an active order")
            messages.info(self.request, 'form is valid')

            return redirect('core:order-summary')


            return redirect('core:checkout')
        messages.warning(self.request, 'please review checkout form')
        return redirect('core:checkout')



class PaymentView(View):
    def get(self, *args, **kwargs):
        payment = Payments.objects.all()
        context = {
            'object': payment
        }
        return render(self.request, 'payment.html', context)

#TODO rework on this payment platform
    def post(self, *args, **kwargs):
        order = Order.objects.get(user= self.request.user, ordered=False)
        token = self.request.POST.get('token')
        amount = order.get_final_price() * 100

        stripe.Charge.create(
            amount=amount,
            currency='ngn',
            source=token
        )


        payment = Payment()
        payment = stripe.Charge.create['id']
        payment.user = self.request.user
        # payment.amount = amount
        # payment.save()

        order.ordered = True
        order.payment = payment
        order.save()




      #   FlutterwaveCheckout({
      #       public_key: "FLWPUBK_TEST-SANDBOXDEMOKEY-X",
      #       tx_ref: "RX1",
      #       amount: 10,
      #       currency: "USD",
      #       country: "US",
      #       payment_options: " ",
      #       redirect_url: "https://callbacks.piedpiper.com/flutterwave.aspx?ismobile=34",
      #       meta: {
      #       consumer_id: 23,
      #       consumer_mac: "92a3-912ba-1192a",
      #        },
      #       customer: {
      #       email: "cornelius@gmail.com",
      #       phone_number: "08102909304",
      #       name: "Flutterwave Developers",
      # },
    #           callback: function (data) {
    #     console.log(data);
    #        },
    #       onclose: function() {
    #     // close modal
    #    },
    #       customizations: {
    #       title: "My store",
    #       description: "Payment for items in cart",
    #       logo: "https://assets.piedpiper.com/logo.png",
    #   },
    # })


def initiate_payment(request : HttpRequest) -> HttpResponse:

    if HttpRequest.method == 'POST':

        payment_form = Payments(request.POST)
        if payment_form.is_valid():
            payment =payment_form.save()
            return render(request, 'newPayment.html', {'payment': payment})

        # else:
        #     payment_form = Payments
        #     return render(request, 'newPayment.html', {'payment_form': payment_form})

class HomeView(ListView):
    model = Item
    paginate_by = 5
    template_name =  'home-page.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered =False)
            context ={
                'object': order
            }
            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "you dont have an active order")
            return redirect('/')




class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


@login_required
def add_to_cart (request, slug):
    item = get_object_or_404(Item, slug= slug)
    order_item, created = OrderItem.objects.get_or_create(item= item,
                                                 user=request.user,
                                                 ordered= False)
    order_qs =Order.objects.filter(user= request.user,
                                   ordered =False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug =item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request, "this item was  quantity updated")
            return redirect('core:order_summary')

        else: 
            messages.info(request, "this item was added to cart")
            order.items.add(order_item)
            return redirect('core:order_summary')

    else:
        order_date = timezone.now()
        order = Order.objects.create(user= request.user, ordered_date= order_date)
        order.items.add(order_item)
    return redirect('core:order_summary')

@login_required
def remove_from_cart (request, slug):
    item = get_object_or_404(Item, slug= slug)
    order_qs =Order.objects.filter(
        user= request.user,
        ordered =False)

    if order_qs.exists():
        order=order_qs[0]
        messages.info(request, "this item  was removed from cart")

        if order.items.filter(item__slug =item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            messages.info(request, "this item was removed from cart")
            order.items.remove(order_item)
            order_item.delete()
            return redirect('core:order_summary')
        else:
            messages.info(request, "this item is not in your cart")
            return redirect('core:product', slug=slug)

    else:
        return redirect('core:product', slug= slug)
    return redirect('core:product', slug=slug)




@login_required
def remove_single_item_from_cart (request, slug):
    item = get_object_or_404(Item, slug= slug)
    order_qs =Order.objects.filter(
        user= request.user,
        ordered =False)

    if order_qs.exists():
        order=order_qs[0]
        messages.info(request, "this item  was removed from cart")

        if order.items.filter(item__slug =item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.quantity -=1
            order_item.save()
            if order_item.quantity == 0:
                order_item.delete()
                order_item.save()
                return redirect('core:home')

            messages.info(request, "this item quantity was update")

            return redirect('core:order_summary')
        else:
            messages.info(request, "this item is not in your cart")
            return redirect('core:product', slug=slug)

    else:
        return redirect('core:product', slug= slug)
    return redirect('core:product', slug=slug)


def add_coupon(request, code):
    try:

        order  = Order.objects.get( user=request.user, ordered=False)
        coupon = Coupon.objects.get( code=code)
    except ObjectDoesNotExist:
        messages.info(request, "you do not have active order")
        return redirect('core:checkout')

