import json
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource("dynamodb")
tabla = dynamodb.Table("ms-workflow-dev")


def lambda_handler(event, context):
    order_id = event["order_id"]
    tenant_id = event.get("tenant_id", "madamtusan")
    paso = event["paso"]
    rol = event["rol"]
    token = event["taskToken"]

    ahora = datetime.now(timezone.utc).isoformat()

    tabla.put_item(
        Item={
            "order_id": order_id,
            "tenant_id": tenant_id,
            "paso_actual": paso,
            "rol_requerido": rol,
            "task_token": token,
            "inicio_paso": ahora,
            "estado_paso": "EN_ESPERA",
        }
    )

    # La maquina queda pausada aqui hasta que completeStep haga SendTaskSuccess
    return {"mensaje": f"Paso {paso} registrado, esperando al {rol}"}