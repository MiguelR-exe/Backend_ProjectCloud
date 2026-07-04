import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(os.environ.get("PRODUCTS_TABLE", "ms-catalog-products-dev"))


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
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