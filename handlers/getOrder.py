import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("ms-orders-orders-dev")


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
        params = event.get("queryStringParameters") or {}
        tenant = params.get("tenant_id", "madamtusan")
        order_id = event["pathParameters"]["id"]
        res = table.get_item(Key={"tenant_id": tenant, "order_id": order_id})
        item = res.get("Item")
        if not item:
            return respond(404, {"error": "Pedido no encontrado"})
        return respond(200, item)
    except Exception as err:
        return respond(500, {"error": str(err)})