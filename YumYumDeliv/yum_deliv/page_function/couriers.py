from yum_deliv.views import database, db
from django.shortcuts import render, redirect
from django.http import JsonResponse


def init(request, uid):
    orders_all = (
        database.collection("orders")
        .stream()
    )
    orders = [order.to_dict() for order in orders_all]
    restaurant = (
        database.collection("restaurant")
        .stream()
    )
    rest = [restaur.to_dict() for restaur in restaurant]
    for ord in orders:
        total_weight = sum(int(dish['weight']) for dish in ord['dishes'])
        ord['total_weight'] = str(total_weight/1000)

        for restaur in rest:
            if restaur['id'] == ord['restaurant']:
                ord['rest_name'] = restaur['name']
                ord['rest_address'] = restaur['address']
                break

    context_courier = {
        "orders": orders,
        "uid": uid,
    }
    redirect(f'/couriers_panel/{uid}')
    return render(request, "Сouriers.html", context=context_courier)


def getOrder(request, uid, order_id):
    order_current = (
        database.collection("orders")
        .where("id", "==", int(order_id))
        .stream()
    )

    data_courier = {
        'courier': uid
    }

    for doc in order_current:
        document_id = doc.id
        db.collection("orders").document(document_id).update(data_courier)

    return JsonResponse({'status': 'ok'})


def markOrderCompleted(request):
    if request.method == 'POST':
        try:
            orderID = request.POST.get('order_id')
            data = {
                'order_status': "Выполнен",
            }
            dish_request = (
                database.collection("orders")
                .where("id", "==", int(orderID))
            )
            docs = dish_request.stream()
            for doc in docs:
                document_id = doc.id
                database.collection("orders").document(document_id).update(data)
            return JsonResponse({'message': f'Статус для заказа({orderID}) был успешно изменен.'})
        except:
            return JsonResponse({'message': 'Критическая ошибка.'})