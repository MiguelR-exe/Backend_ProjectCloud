import json
import boto3

sfn = boto3.client("stepfunctions")

# Pega aqui el ARN de tu maquina (Step Functions -> tu maquina -> State machine ARN)
STATE_MACHINE_ARN = "arn:aws:states:us-east-1:132799337906:stateMachine:workflow-pedidos"


def lambda_handler(event, context):
    try:
        # El pedido viaja en "detail" del evento de EventBridge
        detail = event.get("detail", event)

        sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(detail),
        )
        return {"statusCode": 200, "body": json.dumps({"mensaje": "Workflow iniciado"})}
    except Exception as err:
        print("Error al iniciar workflow:", str(err))
        return {"statusCode": 500, "body": json.dumps({"error": str(err)})}