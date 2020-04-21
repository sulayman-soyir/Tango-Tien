from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, UserForm, UserProfileForm

#assisting function to fill cookie in response
def get_server_side_cookie(request, cookie, default_val = None):
    val =request.session.get(cookie)
    if not val:
        val = default_val
    return val
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    
    request.session['visits'] = visits


# Create your views here.
def index(request):
    #session test
    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories':category_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context = context_dict)
    return response

def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category =Category.objects.get(slug = category_name_slug)

        pages =Page.objects.filter(category = category)
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit = True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form':form})
def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    return HttpResponse("this about page")

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit = False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'rango/register.html',{'user_form': user_form, 'profile_form':profile_form, 'registered' : registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print('post method')
        user = authenticate(username = username, password = password)
        if user:
            if user.is_active:
                login(request, user)
                re_url = reverse('index')
                print(re_url)
                return HttpResponseRedirect(re_url)
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details:{0},{1}".format(username, password))
            return HttpResponse("Invalid login detail supplied.")
    else:
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


