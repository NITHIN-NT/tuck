from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import logging
logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    '''
        This Adapter is used to auto Active the Google authenticated users 
        Saving their Data to the database .
    '''
    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data
        logger.info(f"Social login extra_data: {extra_data}")

        user.first_name = extra_data.get('given_name', '')
        user.last_name = extra_data.get('family_name', '')
        user.profile = extra_data.get('picture', '')

        phone_numbers = extra_data.get('phoneNumbers', [])
        if phone_numbers:
            user.phone = phone_numbers[0].get('value')

        user.is_active = True

        user.save()
        return user



