import json
import os
from decimal import Decimal
import boto3

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(os.environ.get("PRODUCTS_TABLE", "ms-catalog-products-dev"))


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
        product_id = event["pathParameters"]["id"]
        res = tabla.get_item(Key={"product_id": product_id})
        item = res.get("Item")
        if not item:
            return respond(404, {"error": "Producto no encontrado"})
        return respond(200, item)
    except Exception as err:
        return respond(500, {"error": str(err)})
