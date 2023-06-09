from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import auth,messages
from django.contrib.auth.models import User
from userarea.models import *
from django.core.paginator import Paginator
from adminarea.models import *
from adminarea.forms import *
from django.utils.text import slugify
import razorpay
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from razorpay.errors import BadRequestError,ServerError
from django.db.models import Q
from datetime import datetime,timedelta,date
from django.db.models import Sum, F
from django.utils import timezone
import datetime
from django.utils import timezone
from datetime import date, datetime, time
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from userarea.forms import CouponForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_control
from django.template.loader import get_template
import xlwt
# from xhtml2pdf import pisa
# from io import BytesIO


# Create your views here.
def profile(request):
   
   return render(request,'lead/profile.html')

def admin_head(request):
   user_o=request.user.id
   cust=Customer.objects.get(pk=user_o)
   
   return render(request,'head/head.html',locals())
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_panel(request):
        user_o=request.user.id
        cust=Customer.objects.get(pk=user_o)
        rec=Order.objects.all().order_by('-id')
        paginator = Paginator(rec, 5) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        


        today_sales = Payment.objects.filter(created_at=datetime.today(), paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum']
        # Total sales and revenue

        # cust_count = Order.objects.filter(status__in=['Order Confirmed','Shipped', 'Out for delivery','Delivered']).count()
        cust_count = Customer.objects.all().count()
        orders_count = Order.objects.filter(status__in=['Order Confirmed', 'Shipped', 'Out for delivery']).count()
        total_sales = Order.objects.filter(status__in=['Order Confirmed', 'Shipped', 'Out for delivery','Delivered']).count()
        total_revenue = OrderProduct.objects.filter(order__status='Delivered').annotate(total_price=F('product_price') * F('quantity')).aggregate(Sum('total_price'))['total_price__sum']
        # total_revenue = OrderProduct.objects.filter(order__status='Delivered').aggregate(total_revenue=Sum(F('product_price') * F('quantity')))['total_revenue']

        # Render the template with the data
        if today_sales is not None:
            today_sales = round(today_sales,2)
        if total_sales is not None:
            total_sales = round(total_sales)
        if total_revenue is not None:
            total_revenue = round(total_revenue,2)
        cod_sum = Payment.objects.filter(payment_method='COD' ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        cod_sum = round(cod_sum,2)
   
        razorpay_sum = Payment.objects.filter(payment_method='Paid by Razorpay').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        razorpay_sum = round(razorpay_sum, 2)
        allcategory = Category.objects.all()
        
        context = {
                'cust':cust,
                'page_obj': page_obj,
                'cust_count' : cust_count,
                'orders_count': orders_count,
                'today_sales': today_sales,
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'razorpay_sum':razorpay_sum,
                'cod_sum':cod_sum,
                'allcategory':allcategory,
        }
        return render(request,'lead/admin_panel.html', context )

def admin_login(request):
    if request.method=='POST':
        user_name=request.POST['username']
        pass_word=request.POST['password']
        user=auth.authenticate(username=user_name,password=pass_word)
        print(user)
        if user is not None:
           if user.is_superuser:
             auth.login(request,user)
             return redirect('admin_panel')
           else:
            return redirect(admin_login)
        else:
         return redirect(admin_login)


    return render(request,'lead/admin_login.html')

def admin_logout(request):
   auth.logout(request)
   return redirect(admin_login)
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def user_list(request):
    user_o=request.user.id
    cust=Customer.objects.get(pk=user_o)
    user_list = Customer.objects.all().order_by('id')
    paginator = Paginator(user_list, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={
       'page_obj': page_obj,
       'cust':cust,
       }
    return render(request, 'lead/user_list.html', context )

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def blockuser(request, id):
    # user = get_object_or_404(User, id=id)
    user=Customer.objects.get(id=id)
    if user.is_active:
        user.is_active = False
        messages.success(request, "user has been blocked.")
    else:
        user.is_active = True
        messages.success(request, "user has been unblocked.")
    user.save()
    return redirect(user_list)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def products(request):
    user_o=request.user.id
    cust=Customer.objects.get(pk=user_o)
    products_list = Product.objects.all().order_by('-id')
    paginator = Paginator(products_list, 5)  # Show 10 products per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'cust':cust,
    }
   
    return render(request,'lead/product_man.html',context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def add_Product(request):
  user_o=request.user.id
  cust=Customer.objects.get(pk=user_o)
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Product added successfully.')
      return redirect('products')
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('add_Product')
  else:
    form = ProductForm()
    context = {
      'form':form,
      'cust':cust,
    }
    return render(request, 'lead/add_product.html', context)
  
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def edit_Product(request, id):
  user_o=request.user.id
  cust=Customer.objects.get(pk=user_o)

  product = Product.objects.get(id=id)
  
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES, instance=product)
    
    if form.is_valid():
      form.save()
      messages.success(request, 'Product edited successfully.')
      return redirect('products')
    else:
      messages.error(request, 'Invalid input')
      
  form =   ProductForm(instance=product)
  context = {
    'form':form,
    'product':product,
    'cust':cust,

  }
  return render(request, 'lead/product_edit.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def delete_Product(request, id):
  product = Product.objects.get(id=id)
  product.delete()
  return redirect('products')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def category_man(request):
    user_o=request.user.id
    cust=Customer.objects.get(pk=user_o)

    categories = Category.objects.all().order_by('id')
    paginator = Paginator(categories, 5)  # Show 10 categories per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lead/category_man.html', {'page_obj': page_obj,'cust':cust,})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def add_Category(request):
  user_o=request.user.id
  cust=Customer.objects.get(pk=user_o)

  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, 'Category added successfully.')
      return redirect(category_man)
    else:
      messages.error(request, 'Invalid input!!!')
      return redirect('add_Category')
  else:
    form = CategoryForm()
   

    return render(request, 'lead/add_category.html', locals())
  
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def edit_Category(request, category_slug):
    user_o=request.user.id
    cust=Customer.objects.get(pk=user_o)

    # Retrieve the category object using its slug
    category = Category.objects.get(slug=category_slug)

    if request.method == 'POST':
        # Create a form instance with the submitted data and files,
        # and bind it to the category instance
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category edited successfully.')
            return redirect(category_man)
        else:
            # If the form is invalid, display error messages
            messages.error(request, 'Invalid input')

    # Create a new form instance with the category object
    form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'cust':cust,
    }
    return render(request, 'lead/edit_category.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def delete_Category(request, slug):
    category = Category.objects.get(slug=slug)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect(category_man)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def edit_prodect(request,product):
    user_o=request.user.id
    cust=Customer.objects.get(pk=user_o)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
    
        if form.is_valid():
            form.save()
            messages.success(request, 'Product edited successfully.')
        return redirect('products')
    else:
      messages.error(request, 'Invalid input')
      
    form =   ProductForm(instance=product)
    context = {
        'form':form,
        'product':product,
        'cust':cust,
  }

    return render(request,'lead/product_edit.html',context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def delete_prodect(request,product_id):

    dele=Product.objects.get(id=product_id)
    dele.delete()


    return redirect('prodects')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def order_manage(request):
    orders=Order.objects.all().order_by('-id')
    paginator = Paginator(orders, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    
    return render(request, 'lead/orderman.html', locals())

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def orderdetails(request, id):
    order =Order.objects.filter(id=id).first()
    orderitems = OrderProduct.objects.filter(order=order)

    context={
        'order': order,
        'orderitems':orderitems,
    }
    return render(request,'lead/order_details.html',context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admincancelOrder(request, id):

    client = razorpay.Client(auth=("rzp_test_aCOPLFUFmC265M", "xOMWffWBSmuJi5y06YT3aq4N"))
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(order_manage)
    
    payment=order.payment
    msg=''
    
    if (payment.payment_method == 'Paid by Razorpay'):
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount= amount*100
        try :
            captured_amount = client.payment.capture(payment_id,amount)
        except BadRequestError as e:
            # Handle a BadRequestError from Razorpay
            captured_amount = None
            messages.warning(request,'The payment has not been captured,We cant Refund the money')
            return redirect(order_manage)
        #   except ServerError as e:
              # Handle a ServerError from Razorpay
        #   captured_amount = None
            # msg = "Server error occurred while capturing the payment."

        if captured_amount is not None and captured_amount['status'] == 'captured' :
            refund_data = {
                "payment_id": payment_id,
                "amount": amount,  # amount to be refunded in paise
                "currency": "INR",
            }
            
            refund = client.payment.refund(payment_id, refund_data)
            #  except BadRequestError as e:
            #      # Handle a BadRequestError from Razorpay
            #      refund = None
            #      msg = "Bad request error occurred while processing the refund."
            #  except ServerError as e:
            #      # Handle a ServerError from Razorpay
            #      refund = None
            #      msg = "Server error occurred while processing the refund."
            print(refund)
            
            if refund is not None:
                current_user=request.user
                order.refund_completed = True
                order.status = 'Cancelled'
                payment = order.payment
                payment.refund_id = refund['id']
                payment.save()
                order.save()
                messages.success(request,'The order has been successfully cancelled and amount has been refunded!')
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
                messages.warning(request,'The order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'The payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect(order_manage)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def update_order(request, id):
    if request.method == 'POST':
        order = Order.objects.get(id=id)
        status = request.POST.get('status')
        if(status):
            order.status = status
            order.save()
        if status  == "Delivered":
            try:
                payment = Payment.objects.get(payment_id = order.order_number, status = False)
                print(payment)
                if payment.payment_method == 'Cash on Delivery':
                    payment.paid = True
                    payment.save()
            except:
                pass
    return redirect('order_manage')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def searchorder(request):
    keyword = request.GET.get('name')
    print(keyword)
    orders = Order.objects.filter(Q(address__firstname__icontains=keyword) | Q(address__email__icontains=keyword) | Q(status__icontains=keyword) | Q(payment__payment_method__icontains=keyword) | Q(order_number__icontains=keyword)).order_by('-id')
    paginator = Paginator(orders, 8)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    return render(request, 'lead/orderman.html', locals())


def view_coupons(request):
    coupons = Coupon.objects.all()
    return render(request,'lead/view_coupon.html',{'coupons':coupons})

def add_coupons(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(view_coupons)
    else:
        form = CouponForm()
    return render(request, 'lead/add_coupon.html', {'form': form})

def edit_coupon(request, pid):
    coupon = Coupon.objects.get(id=pid)

    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon Updated")
            return redirect(view_coupons)
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'lead/edit_coupon.html', {'form': form, 'coupon': coupon})

def delete_coupon(request, pid):
    coupon = Coupon.objects.get(id=pid)
    coupon.delete()
    messages.success(request, "Coupon Deleted")
    return redirect(view_coupons)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def sales_report(request):
    fro=request.GET.get('from_date')
    to=request.GET.get('to_date')
    
    if fro and to :
        orders = Order.objects.all().order_by('-id')
        today_date = datetime.now().strftime('%Y-%m-%d')

        if 'from_date' in request.GET and 'to_date' in request.GET:
            from_date = request.GET['from_date']
            to_date = request.GET['to_date']

            if to_date > today_date:
                messages.warning(request, "Please select a date up to today's date.")
            elif from_date > to_date:
                messages.warning(request, "The from date should be before than the To date")
            else:
                orders = orders.filter(created_at__range=[from_date, to_date])
                total_sales = orders.aggregate(Sum('paid_amount'))['paid_amount__sum']
    else:
        orders = Order.objects.all().order_by('-id')
       
       
    return render(request, 'lead/sales_report.html', locals())