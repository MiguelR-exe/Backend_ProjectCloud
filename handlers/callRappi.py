import json
import urllib.request

# Cuando tu companero tenga lista la OCI API #2, pega aqui su URL
OCI_API2_URL = "https://TU-OCI-API2/estado"


def lambda_handler(event, context):
    origen = event.get("origen", "web")
    if origen != "rappi":
        return {"mensaje": "Pedido web, no requiere notificar a Rappi"}

    payload = json.dumps({
        "order_id": event.get("order_id"),
        "estado": event.get("paso"),
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            OCI_API2_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"mensaje": "Rappi notificado", "status": resp.status}
    except Exception as err:
        print("Error notificando a Rappi:", str(err))
        return {"mensaje": "No se pudo notificar a Rappi", "error": str(err)}