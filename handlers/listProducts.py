import json
import os
from decimal import Decimal
import boto3

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(os.environ.get("PRODUCTS_TABLE", "ms-catalog-products-dev"))


# Convierte los Decimal de DynamoDB a int o float para poder serializarlos
def decimal_a_num(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False, default=decimal_a_num),
    }


def lambda_handler(event, context):
    try:
        res = tabla.scan()
        productos = res.get("Items", [])
        productos.sort(key=lambda x: (x.get("categoria", ""), x.get("nombre", "")))
        return respond(200, {"total": len(productos), "productos": productos})
    except Exception as err:
        return respond(500, {"error": str(err)})
