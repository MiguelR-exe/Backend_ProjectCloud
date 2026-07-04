import json
import os
from datetime import datetime, timezone
import urllib.request
import boto3

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table(os.environ["WORKFLOW_TABLE"])
sfn = boto3.client("stepfunctions")


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def start_workflow(event, context):
    # Disparado por EventBridge; el pedido viene en detail
    detail = event.get("detail", event)
    sfn.start_execution(
        stateMachineArn=os.environ["STATE_MACHINE_ARN"],
        input=json.dumps(detail),
    )
    return {"mensaje": "Workflow iniciado"}


def registrar_paso(event, context):
    order_id = event["order_id"]
    tenant_id = event.get("tenant_id", "madamtusan")
    paso = event["paso"]
    rol = event["rol"]
    token = event["taskToken"]
    ahora = datetime.now(timezone.utc).isoformat()
    tabla.put_item(Item={
        "order_id": order_id,
        "tenant_id": tenant_id,
        "paso_actual": paso,
        "rol_requerido": rol,
        "task_token": token,
        "inicio_paso": ahora,
        "estado_paso": "EN_ESPERA",
    })
    return {"mensaje": f"Paso {paso} registrado"}


def complete_step(event, context):
    try:
        order_id = event["pathParameters"]["id"]
        body = json.loads(event.get("body") or "{}")
        atendido_por = body.get("atendido_por", "trabajador")
        tenant_id = body.get("tenant_id", "madamtusan")
        res = tabla.get_item(Key={"order_id": order_id, "tenant_id": tenant_id})
        item = res.get("Item")
        if not item or not item.get("task_token"):
            return respond(404, {"error": "No hay paso en espera"})
        token = item["task_token"]
        paso = item["paso_actual"]
        fin = datetime.now(timezone.utc).isoformat()
        sfn.send_task_success(
            taskToken=token,
            output=json.dumps({"paso_completado": paso, "atendido_por": atendido_por}),
        )
        tabla.update_item(
            Key={"order_id": order_id, "tenant_id": tenant_id},
            UpdateExpression="SET estado_paso = :s, atendido_por = :a, fin_paso = :f",
            ExpressionAttributeValues={":s": "COMPLETADO", ":a": atendido_por, ":f": fin},
        )
        return respond(200, {"mensaje": f"Paso {paso} completado por {atendido_por}"})
    except Exception as err:
        return respond(500, {"error": str(err)})


def call_rappi(event, context):
    origen = event.get("origen", "web")
    if origen != "rappi":
        return {"mensaje": "Pedido web, no se notifica"}
    payload = json.dumps({
        "order_id": event.get("order_id"),
        "estado": event.get("paso"),
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            os.environ["OCI_API2_URL"], data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"mensaje": "Rappi notificado", "status": resp.status}
    except Exception as err:
        print("Error notificando Rappi:", str(err))
        return {"mensaje": "No se pudo notificar", "error": str(err)}
