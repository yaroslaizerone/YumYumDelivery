from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import pyrebase

config = {
  "apiKey": "AIzaSyCMk-jWD8RgFoFQSvMfDrjP25qmPwiQK0Q",
  "authDomain": "yumyumdelivery-12ebb.firebaseapp.com",
  "projectId": "yumyumdelivery-12ebb",
  "storageBucket": "yumyumdelivery-12ebb.appspot.com",
  "messagingSenderId": "772726972796",
  "appId": "1:772726972796:web:0eb1ae51194aee6b7204f9"
}


firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


def home(request):
    return TemplateResponse(request, 'homepage.html')


def login_view(request):
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('login')