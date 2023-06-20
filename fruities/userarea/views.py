from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import auth,messages
from django.contrib.auth.models import User
from adminarea.views import *
from userarea.views import *
from userarea.forms import *
from .models import *
# from .forms import *
from django.core.mail import send_mail,EmailMessage
import random
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from razorpay.errors import BadRequestError,ServerError
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
import os
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
# Create your views here.

def home(request):
      # Define with a default value
    
    
        products = Product.objects.all()
       

        # products = Product.objects.filter(id)
        # paginator = Paginator(products, 5)
        # page_number = request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
       

        context = {
        'products': products,
        # 'pro': page_obj,
    }

    
        return render(request,'main/index.html',context)

def static(request):
    
    return render(request,'main/static.html')

def slider(request):
    return render(request,'main/slider.html')

def order(request):

    orders = Order.objects.filter(user=request.user).order_by('-id')

    return render(request, 'main/order.html', {'orders': orders})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            update_session_auth_hash(request, user)
            return redirect(myaccount)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'main/changepass.html', {'form': form})


def login_required_decorator(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

change_password = login_required_decorator(change_password)

def product(request, cid):
    page_obj = None  # Define with a default value
    
    if cid == 0:
        products = Product.objects.all()
       
    else:
        products = Product.objects.filter(id=cid)
        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
       

    context = {
        'products': products,
        'pro': page_obj,
    }

    return render(request, 'main/product.html', context)


def details(request, id):
    pro = Product.objects.get(id=id)

    if pro.stock <= 0:
        # Product is out of stock
        messages.warning(request, 'Sorry, this product is out of stock.')
        return redirect('cart')

    context = {
        'pro': pro,
    }

    return render(request, 'main/singleproduct.html', context)


@never_cache
@login_required(login_url='login')
def add_cart(request):
    if request.method == 'POST': # If form is submitted
        product_id = request.POST['product_id'] # Get product ID from form
        quantity = request.POST['quantity'] # Get quantity from form
        product = Product.objects.get(id=product_id) # Get product object
    if quantity == '0':
        return redirect('cart')
    else:
        try:
            pr_quantity = int(quantity)
        except (TypeError, ValueError):
            pr_quantity = 1

    try:
        cart_item = Cart.objects.get(user=request.user, product=product)
        # If cart item already exists, update the quantity by adding the new quantity
        cart_item.quantity += pr_quantity
        cart_item.save()
    except Cart.DoesNotExist:
        # If cart item doesn't exist, create a new one with the given user, product, and quantity
        cart_item = Cart(user=request.user, product=product, quantity=pr_quantity)
        cart_item.save()

    return redirect('cart')



from django.shortcuts import get_object_or_404
from django.contrib import messages
@never_cache
@login_required(login_url='login')
def cart_update(request):
    cart_id = int(request.POST.get('item_id'))
    product_quantity = int(request.POST.get('product_quantity'))
    cart_item = get_object_or_404(Cart, id=cart_id)
    product = cart_item.product

    try:
        orpro = Product.objects.filter(id=product.id).first()

        cart_item.quantity = product_quantity
        cart_item.save()
       
        

    except Product.DoesNotExist:
        response = JsonResponse({'status':'failed','message':'An order for this product does not exist'})
        return response 
    
    cart_items = Cart.objects.filter(user=request.user)

    '''Calculate subtotal and total'''
    subtotal = 0
    total_items = 0
    for item in cart_items:
        subtotal += item.product.price * item.quantity
        total_items += item.quantity
    
    total = subtotal
    if total_items > 0:
        total = subtotal // total_items

    single_product_total = product.price * cart_item.quantity
    response = JsonResponse({'single_product_total':single_product_total,'sub_total':total, 'grand_total':subtotal})
    return response 



# def decrease_quantity(request, cart_id): # If form is submitted
#         cart_item = Cart.objects.get(id=cart_id) # Get cart item object
#         quantity = cart_item.quantity # Get current quantity

#         if quantity > 1: # Check if quantity is greater than 1
#             quantity -= 1 # Decrease quantity by 1
#             cart_item.quantity = quantity # Update cart item's quantity
#             cart_item.save() # Save the cart item to the database

#         return redirect('cart') 
@never_cache
@login_required(login_url='login')
def remove_cart(request, cart_item_id):
    try:
        cart_item = Cart.objects.get(id=cart_item_id, user=request.user) # Get the cart item with the given ID and user
        cart_item.delete() # Delete the cart item from the database
    except Cart.DoesNotExist:
        pass # If cart item doesn't exist, do nothing

    return redirect('cart')
@never_cache
@login_required(login_url='login')
def cart(request):
    user=request.user
    # Fetch all CartItem objects from the database
    
    cart_items = Cart.objects.filter(user=user)
        

    # Calculate subtotal and total
    subtotal = 0
    total_items = 0
    for item in cart_items:
        subtotal += item.product.price * item.quantity
        total_items += item.quantity
    
    # You can also calculate any other charges or discounts here
    # For example:
    # discount = 10
    # total = subtotal - discount
    
    total = subtotal
    if total_items > 0:
        total = subtotal // total_items
    
    return render(request, 'main/cart.html', {'cr': cart_items, 'subtotal': subtotal, 'total': total,})

def calculateCartTotal(request):
   cart_items   = Cart.objects.filter(user=request.user)
   if not cart_items:
       pass
    #   return redirect('product_management:productlist',0)
   else:
      total = 0
      tax=0
      grand_total=0
      for cart_item in cart_items:
         total  += (cart_item.product.price * cart_item.quantity)
         tax = 50
         grand_total = tax + total
   return total, tax, grand_total


@never_cache
@login_required(login_url='login')
def checkout(request, address_id=None):

    
    subtotal=0
    quantity=0
    amountToBePaid =0
    msg=''
    cart_items=None
    
  
    if address_id:
        addresses = AddressDetails.objects.filter(id=address_id, user_id=request.user)
    else:
        addresses = AddressDetails.objects.filter(user_id=request.user)
    
    user=Customer.objects.get(id=request.user.id)
    cart_items=Cart.objects.filter(user=user, product__stock__gt=0)
    
    for cart_item in cart_items:
        subtotal+=(cart_item.product.price*cart_item.quantity)
        quantity+=cart_item.quantity

    shipping=50
    grand_total = subtotal+shipping
    amountToBePaid = grand_total

   
    
    context={
        'subtotal':subtotal,
        'quantity':quantity,
        'shipping':shipping,
        'cart_items':cart_items,
        'grand_total':grand_total,
        'user':user,
        'amountToBePaid':amountToBePaid,
        'msg':msg,
        'AllAddress':addresses,
        
    }
    return render(request,'main/checkout.html',context)



@never_cache
@login_required(login_url='login')
def confirmation(request, id):

    subtotal=0
    quantity=0
    cart_items=Cart.objects.filter(user=request.user)
    
    addressid = request.POST.get('address')
    
        
    if addressid == None:
            messages.warning(request, "Please Select Your Address,  Or Add A New Address.")
            return redirect(checkout)
    
    address = AddressDetails.objects.get(pk=addressid)
    user = Customer.objects.get(pk=id)

    for cart_item in cart_items:
            subtotal+=(cart_item.product.price*cart_item.quantity)
            quantity+=cart_item.quantity
    shipping=50

    grand_total = subtotal+shipping
    amountToBePaid = grand_total

   
    
    context={
            'subtotal':subtotal,
            'cart_items':cart_items,
            'addressSelected':address,
            'shipping':shipping,
            'amountToBePaid':amountToBePaid,
            'user':user,
            }
    
    return render(request, 'main/confirm.html', context)

@never_cache
@login_required(login_url='login')
def razorPayCheck(request):
   total=0
   amountToBePaid = 0
   current_user=request.user
   cart_items=Cart.objects.filter(user_id=current_user.id)
   if cart_items:
      for cart_item in cart_items:
         total+=(cart_item.product.price*cart_item.quantity)
      tax=50
      grand_total=total+tax
      grand_total = round(grand_total,2)
      amountToBePaid = grand_total
      print()
      return JsonResponse({
         'grand_total' : grand_total,
         'amountToBePaid':amountToBePaid
      })
   else:
      return redirect('filterplace',0)

@never_cache
@login_required(login_url='login')
def placeOrder(request):
   if request.method =='POST':
        #  if ('couponCode' in request.POST):
        #     instance = checkCoupon(request)
        
         instance=None
         cart_items   = Cart.objects.filter(user=request.user)
         if not cart_items:
            return redirect('userproduct',0)
         
         newAddress_id = request.POST.get('addressSelected')
         address  = AddressDetails.objects.get(id = newAddress_id)
         newOrder =Order()
         newOrder.user=request.user
         newOrder.address = address
         yr = int(datetime.date.today().strftime('%Y'))
         dt = int(datetime.date.today().strftime('%d'))
         mt = int(datetime.date.today().strftime('%m'))
         d = datetime.date(yr,mt,dt)
         current_date = d.strftime("%Y%m%d")
         rand = str(random.randint(1111111,9999999))
         order_number = current_date + rand
         newPayment = Payment()
       
         newPayment.payment_id = request.POST.get('payment_id')

         payment_id  =order_number
         newPayment.payment_method = request.POST.get('payment_method')
         newPayment.customer = request.user
         newPayment.save()
         newOrder.payment = newPayment
         total, tax, grand_total = calculateCartTotal(request)
         newOrder.order_total = grand_total
         if(instance):
            if(instance.used == False):
                if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                    amountToBePaid = float(grand_total) - coupon_discount
                    amountToBePaid = format(amountToBePaid, '.2f')
                    coupon_discount = format(coupon_discount, '.2f')
                    newOrder.order_discount = coupon_discount
                    newOrder.paid_amount = amountToBePaid
                    instance.used = True
                    newOrder.paid_amount = amountToBePaid
                    newPayment.amount_paid = amountToBePaid
                    instance.save()
                else:
                    msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
            else:
                newOrder.paid_amount = grand_total
                newPayment.amount_paid = grand_total
                newOrder.discount=0
                msg = 'Coupon is not valid'
         else:
            newOrder.paid_amount = grand_total
            newPayment.amount_paid = grand_total
            msg = 'Coupon not Added'
         newPayment.save()
         newOrder.payment = newPayment
         order_number = 'Fruities'+ order_number
         newOrder.order_number =order_number
         #to making order number unique
         while Order.objects.filter(order_number=order_number) is None:
            order_number = 'Fruities'+order_number
         newOrder.tax=tax
         newOrder.save()
         newPayment.order_id = newOrder.id
         newPayment.save()
         newOrderItems = Cart.objects.filter(user=request.user)
         for item in newOrderItems:
            OrderProduct.objects.create(
                order = newOrder,
                customer=request.user,
                product=item.product,
                product_price=item.product.price,
                quantity=item.quantity
            )
            # product = Product.objects.filter(id=item.product_id).first()
              # Decrease the stock quantity for the product
            product = item.product
            if product.stock < item.quantity:
            # If the product's stock is less than the ordered quantity,
            # handle the appropriate action (e.g., display a message, mark the product as unavailable)
            # You can uncomment and modify this section based on your requirements
                pass
            else:
                product.stock -= item.quantity
                product.save()

            
            # #TO DECRESE THE QUANTITY OF PRODUCT FROM CART
            # orderproduct = Product.objects.filter(id=item.product_id).first()
            # if(orderproduct.stock<=0):
            #     messages.warning(request,'Sorry, Product out of stock!')
            #     orderproduct.is_available = False
            #     orderproduct.save()
            #     item.delete()
            #     return redirect('cart')
            # elif(orderproduct.stock < item.quantity):
            #     messages.success(request,  f"{orderproduct.stock} only left in cart.")
            #     return redirect('cart')
            # else:
            #     orderproduct.stock -=  item.quantity
            # orderproduct.save()
            # if(instance):
            #     instance.order = newOrder
            # instance.save()
        # TO CLEAR THE USER'S CART
            cart_item=Cart.objects.filter(user=request.user)
            cart_item.delete()
            messages.success(request,'Order Placed Successfully')
            payMode =  request.POST.get('payment_method')
            if (payMode == "Paid by Razorpay" ):
                print(order_number,'--------------------order in place order---------------------')

                return JsonResponse ({'ordernumber':order_number,'status':"Your order has been placed successfully"})
            if (payMode == "COD" ):
                request.session['my_context'] = {'payment_id':payment_id}
                return redirect('order_complete', order_number )
            return redirect('checkout')




@never_cache
@login_required(login_url='login')
def orderComplete(request,ordernumber) :
    print(ordernumber,'----------------------ordernumber---------')
    order = Order.objects.get(user=request.user,order_number=ordernumber)
    orderitem = OrderProduct.objects.filter(customer=request.user,order=order)
    
    return render(request,'main/order_completed.html',locals())
@never_cache
@login_required(login_url='login')
def cancelOrder(request):
    if request.method == 'POST':
            id = request.POST.get('id')

    client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("SECRET_KEY")))
    try:
        order = Order.objects.get(id=id,user=request.user)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(order)
    
    payment=order.payment
    msg=''
    
    if (payment.payment_method == 'Paid by Razorpay'):
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount= amount*100
        try :
            # captured_amount = client.payment.capture(payment_id,amount)
            pass
        except BadRequestError as e:
            # Handle a BadRequestError from Razorpay
            captured_amount = None
            messages.warning(request,'The payment has not been captured.Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
            return redirect(order)
        #   except ServerError as e:
              # Handle a ServerError from Razorpay
        #   captured_amount = None
            # msg = "Server error occurred while capturing the payment."

        # if captured_amount is not None and captured_amount['status'] == 'captured' :
        #     refund_data = {
        #         "payment_id": payment_id,
        #         "amount": amount,  # amount to be refunded in paise
        #         "currency": "INR",
        #     }
            
        #     refund = client.payment.refund(payment_id, refund_data)
            #  except BadRequestError as e:
            #      # Handle a BadRequestError from Razorpay
            #      refund = None
            #      msg = "Bad request error occurred while processing the refund."
            #  except ServerError as e:
            #      # Handle a ServerError from Razorpay
            #      refund = None
            #      msg = "Server error occurred while processing the refund."
            # print(refund)
            
            if refund is not None:
                current_user=request.user
                order.refund_completed = True
                order.status = 'Cancelled'
                payment = order.payment
                payment.refund_id = refund['id']
                payment.save()
                order.save()
                messages.success(request,'Your order has been successfully cancelled and amount has been refunded!')
                mess=f'Hai\t{current_user.username},\nYour order has been canceled, Money will be refunded with in 1 hour\nThanks!'
                try:
                    send_mail(
                            "Order Cancelled",
                            mess,
                            settings.EMAIL_HOST_USER,
                            [current_user.email],
                            fail_silently = False
                        )
                except Exception as e:
                    # Handle an exception while sending email
                    msg += "\nError occurred while sending an email notification."
            else :
                messages.warning(request,'Your order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'Your payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect('order')

from django.shortcuts import render, get_object_or_404
from .models import Order, OrderProduct
@never_cache
@login_required(login_url='login')
def viewOrder(request, id):
    order = Order.objects.get(id=id, user=request.user)
    od= OrderProduct.objects.filter(order=order)
   
    return render(request, 'main/view.html',locals())


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth,messages
# from admin_products.models import Product
from .models import Wishlist, WishlistItem
from django.core.exceptions import ObjectDoesNotExist



@never_cache
@login_required(login_url='login')
def _wishlist_id(request):
    wishlist = request.session.session_key
    if not wishlist:
        wishlist = request.session.create()
    return wishlist


from django.shortcuts import get_object_or_404
from django.urls import reverse
@never_cache
@login_required(login_url='login')
def add_wishlist(request,product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        user = request.user
        if WishlistItem.objects.filter(product=product,user_id=user.id).exists():
            messages.warning(request, "Product already exist in wishlist")
            return redirect(wishlist)
            
        else:
            WishlistItem.objects.create(product=product,user_id=user.id)
            messages.success(request,"Product added to wishlist")
            return redirect(wishlist)
            
    else:
        messages.warning(request, "Please log in to add items to wishlist.")
        return redirect('login')
@never_cache
@login_required(login_url='login')
def remove_wishlistitem(request,product_id,wishlist_id):
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        wishlist_item = WishlistItem.objects.get(product=product,user=request.user,id=wishlist_id)
    else:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_item = WishlistItem.objects.get(product=product,wishlist=wishlist)
    wishlist_item.delete()
    messages.success(request, f"{product.product_name} has been removed from the wishlist")
    return redirect('wishlist')

@never_cache
@login_required(login_url='login')
def wishlist(request,wishlist_items=None):
    user=request.user
    wishlist_items=WishlistItem.objects.filter(user_id=user)

    context = {        
        'wishlist_items':wishlist_items,
    }
    
    return render(request, 'main/wishlist.html',context)




def about(request):
    return render(request,'main/about.html')

def contact(request):
    return render(request,'main/contact.html')

def search(request):
  if request.method == 'GET':
    keyword = request.GET['keyword']
    if keyword:
      products = Product.objects.filter(Q(product_name__icontains=keyword))
    #   product_count = products.count()
      
  paginator = Paginator(products,6)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
      
  context = {
    'products':products,
    'pro':page_obj,
    
  }
  return render(request, 'main/product.html', context)
@never_cache
@login_required(login_url='login')
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('manageaddress')
    else:
        form = AddressForm()
    return render(request, 'main/add_address.html', {'form': form})

@never_cache
@login_required(login_url='login')
def confi_add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('checkout')
    else:
        form = AddressForm()
    return render(request, 'main/add_address.html', {'form': form})
@never_cache
@login_required(login_url='login')
def myaccount(request):

    return render(request,'main/myaccount.html')

@never_cache
@login_required(login_url='login')
def updateprofile(request):
    user_id = request.user.id
    user = Customer.objects.get(pk=user_id)

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('myaccount')
        else:
            messages.error(request, 'There was an error while updating your profile.')
    else:
        form = UpdateUserForm(instance=user)
       
    return render(request, 'main/updateprofile.html', locals())
@never_cache
@login_required(login_url='login')
def edit_address(request,id):
    address = get_object_or_404(AddressDetails, id=id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('manageaddress')
    else:
        form = AddressForm(instance=address)

    return render(request, 'main/edit_address.html', {'form': form})
@never_cache
@login_required(login_url='login')
def manageaddress(request):
    user = request.user
    add = AddressDetails.objects.filter(user_id=user.id)
    return render(request, 'main/manageaddress.html', {'add': add})

@never_cache
@login_required(login_url='login')
def deleteaddress(request,id):
    dele=AddressDetails.objects.get(id=id)
    dele.delete()
    return redirect(manageaddress)

def login(request):
    if request.method=='POST':
        user_name=request.POST['username']
        pass_word=request.POST['password']
        user =auth.authenticate(username=user_name,password=pass_word) 
        print(user)
        if user is not None: 
            auth.login(request,user)         
            return redirect(home)
        else:
            return redirect(login)
    return render(request,'main/login.html')

def register(request):
    usr = None
    #Register Form
    if request.method=='POST':
        get_otp=request.POST.get('otp')
        # OTP Verification
        if get_otp:
            get_usr=request.POST.get('usr')
            usr=Customer.objects.get(username=get_usr)
            if int(get_otp)==UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active=True
                usr.save()
                messages.success(request,f'Account is created for {usr.username}')
                return redirect(login)
            else:
                messages.warning(request,f'You Entered a wrong OTP')
                return render(request,'main/register.html',{'otp':True,'usr':usr})
        form = CreateUserForm(request.POST)
        #Form Validation
        if form.is_valid():
            form.save()
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')
            usr=Customer.objects.get(username=username)
            usr.email=email
            usr.username=username
            usr.is_active=False
            usr.save()
            usr_otp=random.randint(100000,999999)
            UserOTP.objects.create(user=usr,otp=usr_otp)
            mess=f'Hello\t{usr.username},\nYour OTP to verify your account for Fruities is {usr_otp}\nThanks!'
            send_mail(
                    "welcome to Fruities -Verify your Email",
                    mess,
                    settings.EMAIL_HOST_USER,
                    [usr.email],
                    fail_silently=False
                )
            messages.info(request,f'OTP send to your email')

            return render(request,'main/register.html',{'otp':True,'usr':usr})
            
        else:
            errors = form.errors
            for field, errors in errors.items():
              for error in errors:
                messages.error(request, f" {error}")
                       
    #Resend OTP
    elif (request.method == "GET" and 'username' in request.GET):
        get_usr = request.GET['username']
        if (Customer.objects.filter(username = get_usr).exists() and not Customer.objects.get(username = get_usr).is_active):
            usr = Customer.objects.get(username=get_usr)
            id = usr.id
            
            otp_usr = UserOTP.objects.get(user_id=id)
            usr_otp=otp_usr.otp
            mess = f"Hello, {usr.username},\nYour OTP is {usr_otp}\nThanks!"
            
            send_mail(
        "Welcome to Fruities - Verify Your Email",
        mess,
        settings.EMAIL_HOST_USER,
        [usr.email],
        messages.success(request, f'OTP resend to  {usr.email}'),

        # fail_silently = False
         )
        return render(request,'main/register.html',{'otp':True,'usr':usr})
    else:
            errors = ''
    form=CreateUserForm()
    context = {'form': form, 'errors': errors}

    return render (request, 'main/register.html', context)

def logout(request):
    auth.logout(request)
    # if 'username' in request.session:
    #     request.session.flush()
    return redirect(home)

def forgetpassword(request):
    if request.method=="POST":
        email=request.POST['email']
        if Customer.objects.filter(email=email).exists():
            user=Customer.objects.get(email__exact=email)
           #reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('main/resetpassemail.html', {
                'user': user,
                'domain': current_site,
             
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                 # Generate a token for a user also
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email=EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            send_email.send()

            messages.success(request,"Password reset email has been sent to your email")
            
            return redirect(login)
        else:
            messages.error(request,'Account does not exists')
            return redirect('login')
    return render(request,'main/forgetpassword.html')

    
def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Customer._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,Customer.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,"  Please reset your password")
        return redirect('resetpassword')
    else:
        messages.error(request,"This link has been expired")
        return redirect('login')
    

def resetpassword(request):
   if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password == confirm_password:
            uid=request.session.get('uid')
            user= Customer.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")
            return redirect('login')
        else:
          messages.error(request,"Password not match")
          return redirect('resetPassword')
   else:
     return render (request,'main/resetPassword.html')


# def error_404(request, exception):
#    context = {}
#    return render(request,'404.html', context)

