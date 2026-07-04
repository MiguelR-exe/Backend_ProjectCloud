import json
import boto3
from boto3.dynamodb.conditions import Key

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
        tenant = params.get("tenant_id")
        if tenant:
            res = table.query(KeyConditionExpression=Key("tenant_id").eq(tenant))
        else:
            res = table.scan()
        items = res.get("Items", [])
        items.sort(key=lambda x: x.get("creado_en", ""))
        return respond(200, {"total": len(items), "pedidos": items})
    except Exception as err:
        return respond(500, {"error": str(err)})