from django import forms
from django.forms import inlineformset_factory
from  products.models import Product,ProductVariant,ProductImage,Size,Category

class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
class AdminForgotPasswordEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))


class AdminVerifyOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6
    )

class AdminSetNewPassword(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match.")
            
        return cleaned_data
class AdminProductAddForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 
            'category', 
            'base_price', 
            'offer_price', 
            'description', 
            'is_featured', 
            'is_selective', 
            'is_most_demanded', 
            'is_blocked'

        ]
        widgets = {
            'name': forms.TextInput(attrs={  
                'id': 'product_name',  
                'required': True
            }),
            'category': forms.Select(attrs={
                'id': 'category', 
                'required': True
            }),
            'base_price': forms.NumberInput(attrs={
                'id': 'base_price', 
                'step': '0.01', 
                'required': True
            }),
            'offer_price': forms.NumberInput(attrs={
                'id': 'offer_price', 
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'id': 'description', 
                'rows': 6
            }),
            # Checkboxes
            'is_featured': forms.CheckboxInput(attrs={'id': 'is_featured'}),
            'is_selective': forms.CheckboxInput(attrs={'id': 'is_selective'}),
            'is_most_demanded': forms.CheckboxInput(attrs={'id': 'is_most_demanded'}),
            'is_blocked': forms.CheckboxInput(attrs={'id': 'is_blocked'}),
        }


class VariantForm(forms.ModelForm):
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        widget=forms.Select(attrs={'class': 'variant-size', 'required': True})
    )

    class Meta:
        model = ProductVariant
        fields = ['size', 'price', 'stock']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'variant-price', 'step': '0.01', 'required': True}),
            'stock': forms.NumberInput(attrs={'class': 'variant-stock', 'min': '0', 'required': True}),
        }

class ImageForm(forms.ModelForm):
    extra_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'gallery-image', 'required': True, 'accept': 'image/*'}),
        label="Image File" 
    )
    alt_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'gallery-alt-text', 'placeholder': 'Describe the image'}),
        required=False 
    )
    class Meta:
        model = ProductImage
        fields = ['extra_image','alt_text'] 

# --- Formsets ---
VariantFormSet = inlineformset_factory(
    Product, 
    ProductVariant, 
    form=VariantForm, 
    extra=1,
    can_delete=True,
    can_delete_extra=True
)

ImageFormSet = inlineformset_factory(
    Product, 
    ProductImage, 
    form=ImageForm, 
    extra=1,
    can_delete=True,
    can_delete_extra=True
)