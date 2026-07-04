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
        res = tabla.scan()
        productos = res.get("Items", [])
        # ordenar por categoria y luego por nombre
        productos.sort(key=lambda x: (x.get("categoria", ""), x.get("nombre", "")))
        return respond(200, {"total": len(productos), "productos": productos})
    except Exception as err:
        return respond(500, {"error": str(err)})