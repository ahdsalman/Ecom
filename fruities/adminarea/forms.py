from django import forms
from .models import *
from django.utils.safestring import mark_safe


class CategoryForm(forms.ModelForm):
    class Meta:
         model = Category
         fields = ['category_name', 'slug','description', 'cat_image',]
        
    def __init__(self, *args, **kwargs):
        super(CategoryForm,self).__init__(*args, **kwargs)
        for field  in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'







class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'unit', 'image_1', 'image_2', 'image_3', 'image_4', 'stock',
                  'is_available', 'is_featured', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['min'] = 0
        self.fields['stock'].widget.attrs['min'] = 0
        self.fields['category'].widget.attrs['onchange'] = "getval(this);"
        self.fields['is_available'].widget.attrs['class'] = 'form-check-input small-checkbox'
        self.fields['is_featured'].widget.attrs['class'] = 'form-check-input small-checkbox'
        

        for field_name, field in self.fields.items():
            classes = field.widget.attrs.get('class', '')
            classes += ' form-control'
            field.widget.attrs['class'] = classes.strip()

        # Add Bootstrap styles to the form labels
        self.label_suffix = mark_safe('<span class="text-primary">*</span>')
 