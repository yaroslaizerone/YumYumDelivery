from yum_deliv.views import homepageContext
from django.shortcuts import render
from django.http import HttpResponseServerError


def home(request):
    # try:
        context = homepageContext(request)
        return render(request, "Homepage.html", context)
    # except Exception as e:
    #     print(f"An error occurred: {str(e)}")
    #     return HttpResponseServerError("Internal Server Error", content_type="text/plain")