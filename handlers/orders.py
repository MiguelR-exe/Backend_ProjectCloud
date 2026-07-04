import json
import os
import uuid
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(os.environ["ORDERS_TABLE"])
events = boto3.client("events")


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def create_order(event, context):
    try:
        data = json.loads(event.get("body") or "{}")
        order = {
            "tenant_id": data.get("tenant_id", "madamtusan"),
            "order_id": str(uuid.uuid4()),
            "origen": data.get("origen", "web"),
            "items": data.get("items", []),
            "cliente": data.get("cliente", "anonimo"),
            "estado": "RECIBIDO",
            "creado_en": datetime.now(timezone.utc).isoformat(),
        }
        tabla.put_item(Item=order)
        events.put_events(Entries=[{
            "Source": "madamtusan.orders",
            "DetailType": "PedidoCreado",
            "Detail": json.dumps(order),
            "EventBusName": "default",
        }])
        return respond(201, {"mensaje": "Pedido creado", "order": order})
    except Exception as err:
        return respond(500, {"error": str(err)})


def get_order(event, context):
    try:
        tenant = (event.get("queryStringParameters") or {}).get("tenant_id", "madamtusan")
        order_id = event["pathParameters"]["id"]
        res = tabla.get_item(Key={"tenant_id": tenant, "order_id": order_id})
        item = res.get("Item")
        if not item:
            return respond(404, {"error": "Pedido no encontrado"})
        return respond(200, item)
    except Exception as err:
        return respond(500, {"error": str(err)})


def list_orders(event, context):
    try:
        from boto3.dynamodb.conditions import Key
        tenant = (event.get("queryStringParameters") or {}).get("tenant_id")
        if tenant:
            res = tabla.query(KeyConditionExpression=Key("tenant_id").eq(tenant))
        else:
            res = tabla.scan()
        items = res.get("Items", [])
        items.sort(key=lambda x: x.get("creado_en", ""))
        return respond(200, {"total": len(items), "pedidos": items})
    except Exception as err:
        return respond(500, {"error": str(err)})
