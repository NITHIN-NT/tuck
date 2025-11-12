from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

'''
class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to modify default user signup/login behavior.
    """
    def get_login_redirect_url(self, request):
        """
        Redirect to home page after login
        """
        return reverse("Home_page_user")

    def save_user(self, request, user, form, commit=True):
        user =  super().save_user(request, user, form, commit=False)
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.phone = form.cleaned_data.get('phone')
        user.is_active = True

        if commit:
            user.save()
        return user
    
    def is_open_for_signup(self, request):
        return True
'''

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self,request,sociallogin,form=None):
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data

        user.first_name = extra_data.get('first_name','')   
        user.last_name = extra_data.get('last_name','')

        user.is_active = True
        user.save()
        return super().save_user(request,sociallogin,form)



