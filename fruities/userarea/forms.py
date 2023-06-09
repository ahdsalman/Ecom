from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm



#regitration

class CreateUserForm(UserCreationForm):
   password1=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password',                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}))
   password2=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password',                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}))
   class Meta:
        model = Customer
        fields = ['username', 'email','password1', 'password2']
        widgets = { 
            'username': forms.TextInput(attrs=
                                        {'placeholder': 'First Name',
                                         'class':'form-control',
                                         'style':'max-width:300px; margin-left:115px'
                                         
                                         }),
            'email': forms.TextInput(attrs={'placeholder': 'Email',
                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}),
            
             }


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'pincode', 'city', 'state', 'profile_pic']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter Your First Name','class':'form-control'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter Your email','class':'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Your Last Name','class':'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Your Phone Number','class':'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Your Address','class':'form-control'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter Your State','class':'form-control'}),
            'pincode': forms.NumberInput(attrs={'placeholder': 'Enter Your Pincode','class':'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter Your City','class':'form-control'}),




         }


        
form = UpdateUserForm(initial={'city': Customer.username})

class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressDetails
        fields = ('first_name', 'last_name', 'phone', 'email', 'order_address', 'city', 'state', 'country', 'zip_code')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter Your First Name','class':'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Your Last Name','class':'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Your Phone Number','class':'form-control'}),
            'country': forms.TextInput(attrs={'placeholder': 'Enter Your Address','class':'form-control'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter Your State','class':'form-control'}),
            'zip_code': forms.NumberInput(attrs={'placeholder': 'Enter Your Pincode','class':'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter Your City','class':'form-control'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter Your Email','class':'form-control'}),
            'order_address': forms.TextInput(attrs={'placeholder': 'Landmark','class':'form-control'}),
            
            
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount', 'min_value', 'valid_from', 'valid_at', 'active']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local','placeholder': 'First Name', 'class':'form-control','style':'max-width:300px; margin-left:115px'}),
            'valid_at': forms.DateTimeInput(attrs={'type': 'datetime-local','placeholder': 'First Name','class':'form-control', 'style':'max-width:300px; margin-left:115px'}),
            'code': forms.TextInput(attrs={'placeholder': 'Coupon code', 'class': 'form-control','style':'max-width:300px; margin-left:115px'}),
            'discount': forms.TextInput(attrs={'placeholder': 'Discount', 'class': 'form-control','style':'max-width:300px; margin-left:115px'}),
            'min_value': forms.TextInput(attrs={'placeholder': 'Minimum value', 'class': 'form-control','style':'max-width:300px; margin-left:115px'}),
        }

