from yum_deliv.views import homepage_context
from django.shortcuts import render
from django.http import HttpResponseServerError


def home(request):
    try:
        context = homepage_context(request)
        return render(request, "Homepage.html", context)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HttpResponseServerError("Internal Server Error", content_type="text/plain")