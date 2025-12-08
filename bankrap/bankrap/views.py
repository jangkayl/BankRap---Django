from django.shortcuts import render

def index_view(request):
    return render(request, 'index.html')

def login_view(request):
    # Logic will go here later, for now just show the template
    return render(request, 'login.html')

def register_view(request):
    # Logic will go here later, for now just show the template
    return render(request, 'register.html')