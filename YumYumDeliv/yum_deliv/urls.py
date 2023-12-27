from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # URLs Авторизации
    path('postsignIn/', views.postsignIn),
    path('signUp/', views.signUp, name="signup"),
    path('logout/', views.logout, name="log"),
    path('postsignUp/', views.postsignUp),
    # Сброс пароля
    path('reset/', views.reset),
    path('postReset/', views.postReset),
    # URLs администратора
    path('adminRest/<slug:rest_slug>', views.adminRest, name="adminRest"),
    path('add_dish/<slug:rest_slug>', views.add_dish, name="add_dish"),
    path('republuc/<slug:rest_slug>', views.republuc, name="republuc"),
    # URL ресторана
    path('restaurant/<slug:url_rest>', views.restaurant, name="restaurant"),
    # URL Оплаты
    path('place_order/', views.place_order, name='place_order'),
    path('cart/', views.ordered, name='ordered'),
    path('payOfOrder/', views.payOfOrder, name='payOfOrder')
]