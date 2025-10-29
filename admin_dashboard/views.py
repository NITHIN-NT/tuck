from django.shortcuts import render,HttpResponse

# Create your views here.
def admin_home(request):
    return render(request,'dashboard/dashboard.html')

def admin_user_view(request):
    return render(request,'users/home_user.html')

def admin_user_edit(request):
    return render(request,'users/edit_user.html')

def admin_user_add(request):
    return render(request,'users/add_user.html')

def admin_products_view(request):
    return render(request,'products/products_admin.html')

# def admin_user_edit(request):
#     return render(request,'users/edit_user.html')

# def admin_user_add(request):
#     return render(request,'users/add_user.html')

def admin_category_view(request):
    return render(request,'categorys/category.html')

# def admin_user_edit(request):
#     return render(request,'users/edit_user.html')

# def admin_user_add(request):
#     return render(request,'users/add_user.html')


