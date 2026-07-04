import json
import uuid
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("ms-orders-orders-dev")
events = boto3.client("events")


def respond(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


def lambda_handler(event, context):
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
        table.put_item(Item=order)

        # Publicar evento a EventBridge para arrancar el workflow
        events.put_events(
            Entries=[
                {
                    "Source": "madamtusan.orders",
                    "DetailType": "PedidoCreado",
                    "Detail": json.dumps(order),
                    "EventBusName": "default",
                }
            ]
        )

        return respond(201, {"mensaje": "Pedido creado", "order": order})
    except Exception as err:
        return respond(500, {"error": str(err)})