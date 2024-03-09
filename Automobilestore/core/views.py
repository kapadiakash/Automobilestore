from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from . models import Customer,Automobile,Order,Cart
from . forms import RegistrationForm,AuthenticateForm,ChangePasswordForm,UserProfileForm,AdminProfileForm,CustomerForm
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.db.models import F
from django.contrib.auth.models import User

# Create your views here.
# def home(request):
#     return render(request, 'core/home.html')

# --- Clased Based View of Home ---
class HomeView(View):
    def get(self,request):
        return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')

# --- Function Based View of scooty_categories---
# def scooty_categories(request):
#     return render(request,'core/scooty_categories.html')

#=========================================================================================================

#--- Class Based View of scooty_categories ---
class scootyCategoriesView(View):
    def get(self,request):
        scooty_category = Automobile.objects.filter(category='scooty')  # we are using filter function of queryset, that will filter those data whose category belongs to scooty
        return render(request,'core/scooty_categories.html',{'scooty_category':scooty_category})


# --- Function Based View of super_categories---
# def super_categories(request):
#     return render(request,'core/super_categories.html')

#--- Class Based View of super_categories ---
class superCategoriesView(View):
    def get(self,request):
        super_category = Automobile.objects.filter(category='SUPER')  # we are using filter function of queryset, that will filter those data whose category belongs to scooty
        return render(request,'core/super_categories.html',{'super_category':super_category})


def bike_categories(request):
    return render(request,'core/bike_categories.html')

#=========================================================================================================
# def Automobile_details(request):
#     return render(request,'core/Automobile_details.html')

class AutomobileDetailView(View):
    def get(self,request,id):     # id = It will fetch id of particular Automobile 
        Automobile = Automobile.objects.get(pk=id)

        #------ code for caculate percentage -----
        if Automobile.discounted_price !=0:    # fetch discount price of particular Automobile
            percentage = int(((Automobile.selling_price-Automobile.discounted_price)/Automobile.selling_price)*100)
        else:
            percentage = 0
        # ------ code end for caculate percentage ---------
            
        return render(request,'core/Automobile_details.html',{'Automobile':Automobile,'percentage':percentage})


#============================== Registration ==========================================================


def registration(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            mf = RegistrationForm(request.POST)
            if mf.is_valid():
                mf.save()
                return redirect('registration')    
        else:
            mf  = RegistrationForm()
        return render(request,'core/registration.html',{'mf':mf})
    else:
        return redirect('profile')


#============================== Login ==========================================================

def log_in(request):
    if not request.user.is_authenticated:  # check whether user is not login ,if so it will show login option
        if request.method == 'POST':       # otherwise it will redirect to the profile page 
            mf = AuthenticateForm(request,request.POST)
            if mf.is_valid():
                name = mf.cleaned_data['username']
                pas = mf.cleaned_data['password']
                user = authenticate(username=name, password=pas)
                if user is not None:
                    login(request, user)
                    return redirect('/')
        else:
            mf = AuthenticateForm()
        return render(request,'core/login.html',{'mf':mf})
    else:
        return redirect('profile')
    

#================================= Profile ====================================================

def profile(request):
    if request.user.is_authenticated:  # This check wheter user is login, if not it will redirect to login page
        if request.method == 'POST':
            if request.user.is_superuser == True:
                mf = AdminProfileForm(request.POST,instance=request.user)
            else:
                mf = UserProfileForm(request.POST,instance=request.user)
            if mf.is_valid():
                mf.save()
        else:
            if request.user.is_superuser == True:
                mf = AdminProfileForm(instance=request.user)
            else:
                mf = UserProfileForm(instance=request.user)
        return render(request,'core/profile.html',{'name':request.user,'mf':mf})
    else:                                                # request.user returns the username
        return redirect('login')


#================================= Logout ====================================================

def log_out(request):
    logout(request)
    return redirect('home')


#================================= Change Password =============================================


def changepassword(request):                                       # Password Change Form               
    if request.user.is_authenticated:                              # Include old password 
        if request.method == 'POST':                               
            mf =ChangePasswordForm(request.user,request.POST)
            if mf.is_valid():
                mf.save()
                update_session_auth_hash(request,mf.user)
                return redirect('profile')
        else:
            mf = ChangePasswordForm(request.user)
        return render(request,'core/changepassword.html',{'mf':mf})
    else:
        return redirect('login')
    

#=========================== Add TO Cart Section =================================================
    
def add_to_cart(request, id):    # This 'id' is coming from 'Automobile.id' which hold the id of current Automobile , which is passing through {% url 'addtocart' Automobile.id %} from Automobile_detail.html 
    if request.user.is_authenticated:
        product = Automobile.objects.get(pk=id) # product variable is holding data of current object which is passed through 'id' from parameter
        user=request.user                # user variable store the current user i.e steveroger
        Cart(user=user,product=product).save()  # In cart model current user i.e steveroger will save in user variable and current Automobile object will be save in product variable
        return redirect('Automobiledetails', id)       # finally it will redirect to Automobile_details.html with current object 'id' to display Automobile after adding to the cart
    else:
        return redirect('login')                # If user is not login it will redirect to login page

def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)      # cart_items will fetch product of current user, and show product available in the cart of the current user.
    total =0
    delhivery_charge =2000
    for item in cart_items:
        item.product.price_and_quantity_total = item.product.discounted_price * item.quantity
        total += item.product.price_and_quantity_total
    final_price= delhivery_charge + total
    return render(request, 'core/view_cart.html', {'cart_items': cart_items,'total':total,'final_price':final_price})

def add_quantity(request, id):
    product = get_object_or_404(Cart, pk=id)    # If the object is found, it returns the object. If not, it raises an HTTP 404 exception (Http404).
    product.quantity += 1                       # If object found it will be add 1 quantity to the current object   
    product.save()
    return redirect('viewcart')

def delete_quantity(request, id):
    product = get_object_or_404(Cart, pk=id)
    if product.quantity > 1:
        product.quantity -= 1
        product.save() 
    return redirect('viewcart')

def delete_cart(request,id):
    if request.method == 'POST':
        de = Cart.objects.get(pk=id)
        de.delete()
    return redirect('viewcart')

#===================================== Checkout ============================================

def checkout(request):
    pass

#===================================== Address ============================================

def address(request):
    if request.method == 'POST':
            print(request.user)
            mf =CustomerForm(request.POST)
            print('mf',mf)
            if mf.is_valid():
                user=request.user                # user variable store the current user i.e steveroger
                name= mf.cleaned_data['name']
                address= mf.cleaned_data['address']
                city= mf.cleaned_data['city']
                state= mf.cleaned_data['state']
                pincode= mf.cleaned_data['pincode']
                print(state)
                print(city)
                print(name)
                Customer(user=user,name=name,address=address,city=city,state=state,pincode=pincode).save()
                return redirect('address')           
    else:
        mf =CustomerForm()
        address = Customer.objects.filter(user=request.user)
        print(address)
    return render(request,'core/address.html',{'mf':mf,'address':address})


def delete_address(request,id):
    if request.method == 'POST':
        de = Customer.objects.get(pk=id)
        de.delete()
    return redirect('address')