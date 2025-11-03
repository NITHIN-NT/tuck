from django.contrib.auth.decorators import user_passes_test

def superuser_required(view_func=None,login_url=''):
    """
        allow only superusers
    """ 
    actual_decorator = user_passes_test(lambda user:user.is_superuser,login_url=login_url)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
