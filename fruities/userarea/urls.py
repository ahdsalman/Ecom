from django.urls import path,include
from .import views
# from django.conf.urls import handler404


urlpatterns = [
    
    path('',views.home,name='home'),
    path('static/',views.static,name='static'),
    path('slider/',views.slider,name='slider'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('product/<int:cid>/',views.product,name='product'),
    path('search/',views. search,name='search'),
    path('details/<int:id>/',views. details,name='details'),

    path('cart/',views.cart,name='cart'),
    path('add-to-cart/', views.add_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/',views. remove_cart, name='remove_cart'),

    path('checkout/',views.checkout,name='checkout'),
    path('logout/',views.logout,name='logout'),
    path('login/',views.login,name='login'),
    path('forgetpassword/',views.forgetpassword,name='forgetpassword'),
    path('register/',views.register,name='register'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),

    path('cart/increase/',views. cart_update, name='cart-update'),
    # path('cart/decrease/<int:cart_id>/',views. decrease_quantity, name='decrease_quantity'),

    path('add_address/',views.add_address,name='add_address'),
    path('updateprofile/', views.updateprofile, name='updateprofile'),
    path('manageaddress/',views.manageaddress,name='manageaddress'),
    path('deleteaddress/<int:id>/',views.deleteaddress,name='deleteaddress'),
    path('edit_address/<int:id>/', views.edit_address, name='editaddress'),
    path('myaccount/',views.myaccount,name='myaccount'),
    path('confirmation/<int:id>',views. confirmation, name='confirmation'),
    path('checkout/',views.checkout, name='checkout'),
    path('placeorder/', views.placeOrder, name='place_order'),
    path('ordercomplete/<str:ordernumber>/',views.orderComplete, name='order_complete'),
    # path('order/',views.order,name='order'),
    path('cancelOrder/',views.cancelOrder, name='cancelOrder'),
    path('order/', views.order, name='order'),
    path('vieworder/<int:id>/',views.viewOrder, name='vieworder'),

    # path('vieworder/<int:order_id>/', views.viewOrder, name='view_order'),
    # path('vieworder/<int:id>/',views.viewOrder, name='vieworder'),
    path('change_password/',views. change_password, name='change_password'),
    path('confi_add_address/',views. confi_add_address, name='confi_add_address'),
    
    path('wishlist/',views. wishlist, name='wishlist'),    
    path('add_wishlist/<int:product_id>/',views. add_wishlist, name='add_wishlist'),    
    path('remove_wishlistitem/<int:product_id>/<int:wishlist_id>/',views. remove_wishlistitem, name='remove_wishlistitem'),
    path('proceed_to_pay/',views.razorPayCheck,name='razorpaycheck'),
   
    
    


]
# handler404 =views.error_404