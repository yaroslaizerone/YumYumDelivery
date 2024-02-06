from django.urls import path
from . import views
from .page_function import homepage, user_functions, admin_rest, operator, couriers

urlpatterns = [
    path('', homepage.home, name='home'),
    # URLs Авторизации
    path('postsignIn/', views.postsignIn),
    path('signUp/', views.signUp, name="signup"),
    path('logout/', views.logOut, name="log"),
    path('postsignUp/', views.postsignUp),
    # Сброс пароля
    path('reset/', views.reset),
    path('postReset/', views.postReset),
    # URLs Администратора ресторана
    path('adminRest/<slug:rest_slug>', views.adminRest, name="adminRest"),
    path('add_dish/<slug:rest_slug>', admin_rest.addDish, name="add_dish"),
    path('republic/<slug:rest_slug>', admin_rest.republic, name="republic"),
    path('delete_dish/<slug:rest>/<slug:dish_id>', admin_rest.deleteDish, name='delete_dish'),
    path('edit/<slug:rest>/<slug:dish_id>', admin_rest.editDish, name='edit_dish'),
    path('change_status/<slug:rest>/<slug:order_id>', admin_rest.changeStatus, name='change_status'),
    # URLs Ресторана
    path('restaurant/<slug:url_rest>', admin_rest.restaurant, name="restaurant"),
    # URLs Оплаты
    path('place_order/', views.placeOrder, name='place_order'),
    path('ordered/<slug:url_rest>', views.ordered, name='ordered'),
    path('payOfOrder/<slug:url_rest>', views.payOfOrder, name='payOfOrder'),
    path('public_order/', views.publicOrder,  name='publucOrder'),
    # URLs Пользователя
    path('orders/<slug:uid>', views.orders, name="orders"),
    path('update_user_data/<slug:uid>', user_functions.updateUserData, name="updata_user_data"),
    path('user_add_address/<slug:uid>', user_functions.userAddress, name="user_address"),
    path('delete_address/<slug:addressID>', user_functions.deleteAddress, name="delete_address"),
    path('createsupport/<slug:uid>', user_functions.createSupport, name='createsupport'),
    path('delete_order/<slug:uid>/<slug:order_id>', user_functions.deleteOrder, name='deleteorder'),
    # URLs Оператора
    path('operator_panel/', operator.init, name='oper'),
    path('sendResponse/<slug:feedback>', operator.sendResponse, name='sendResponse'),
    #URLs Курьера
    path('couriers_panel/<slug:uid>', couriers.init, name='couriers'),
    path('get_order/<slug:uid>/<slug:order_id>', couriers.getOrder, name='getOrder'),
]