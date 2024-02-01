from yum_deliv.views import database, db
from django.shortcuts import render, redirect
from django.http import JsonResponse


def init(request, uid):
    orders_all = (
        database.collection("orders")
        .stream()
    )
    orders = [order.to_dict() for order in orders_all]
    for ord in orders:
        total_weight = sum(int(dish['weight']) for dish in ord['dishes'])
        ord['total_weight'] = str(total_weight/1000)

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