import json
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table("ms-workflow-dev")
sfn = boto3.client("stepfunctions")


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
        order_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body") or "{}")
        atendido_por = body.get("atendido_por", "trabajador")
        tenant_id = body.get("tenant_id", "madamtusan")

        # 1. Recuperar el token guardado
        res = tabla.get_item(Key={"order_id": order_id, "tenant_id": tenant_id})
        item = res.get("Item")
        if not item or not item.get("task_token"):
            return respond(404, {"error": "No hay un paso en espera para este pedido"})

        token = item["task_token"]
        paso = item["paso_actual"]
        fin = datetime.now(timezone.utc).isoformat()

        # 2. Despertar la maquina
        sfn.send_task_success(
            taskToken=token,
            output=json.dumps({"paso_completado": paso, "atendido_por": atendido_por}),
        )

        # 3. Registrar quien atendio y el fin del paso
        tabla.update_item(
            Key={"order_id": order_id, "tenant_id": tenant_id},
            UpdateExpression="SET estado_paso = :s, atendido_por = :a, fin_paso = :f",
            ExpressionAttributeValues={
                ":s": "COMPLETADO",
                ":a": atendido_por,
                ":f": fin,
            },
        )

        return respond(200, {
            "mensaje": f"Paso {paso} completado por {atendido_por}",
            "order_id": order_id,
        })
    except Exception as err:
        return respond(500, {"error": str(err)})