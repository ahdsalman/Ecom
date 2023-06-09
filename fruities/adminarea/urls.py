from django.urls import path,include
from .import views


urlpatterns = [
    path('admin_panel/', views.admin_panel,name='admin_panel'),
    path('head/', views.admin_head,name='head'),

    path('admin_login/', views.admin_login,name='admin_login'),
    path('admin_logout/', views.admin_logout,name='admin_logout'),
    path('user_list/',views.user_list,name='user_list'),
    path('<int:id>/blockuser/', views.blockuser, name='blockuser'),
    path('profile/',views.profile,name='profile'),


    path('products/', views.products,name='products'),
    path('add_product/', views.add_Product,name='add_product'),
    path('<int:id>/edit_Product/', views.edit_Product, name='edit_Product'),
    path('<int:id>/delete_Product/', views.delete_Product, name='delete_Product'),
    path('order_manage/',views.order_manage, name="order_manage"),
    path('orderdetails/<int:id>/',views. orderdetails, name="orderdetails"),
    path('admincancelOrder/<int:id>/',views.admincancelOrder, name='admincancelOrder'),
    path('searchorder/',views. searchorder, name="searchorder"),
    path('update_order/<int:id>/',views. update_order, name="update_order"),



    path('category_man/', views.category_man,name='category_man'),
    path('add_category/', views.add_Category,name='add_category'),
    path('<slug:category_slug>/edit_Category/', views.edit_Category, name='edit_Category'),
    path('<str:slug>/delete_Category/', views.delete_Category, name='delete_Category'),

    path('viewcoupon/',views.view_coupons,name="viewcoupon"),
    path('addcoupon/',views.add_coupons,name="addcoupon"),
    path('editcoupon/<int:pid>/',views.edit_coupon,name="editcoupon"),
    path('deletecoupon/<int:pid>/',views.delete_coupon,name="deletecoupon"),
    

    path('salesreport/',views.sales_report,name="salesreport"),
    # path('sales_report/',views.sales_report,name="sales_report"),
    # path('sales_report_month/<int:id>',views.sales_report_month,name="sales_report_month"),
    # path("sales_report_year/<int:id>",views.sales_report_year,name='sales_report_year'),
    
    # path('pdf_report/<str:start_date>//<str:end_date>/', views.pdf_report, name='pdf_report'),  
    # path('excel_report/<str:start_date>//<str:end_date>/', views.excel_report, name='excel_report')


]
