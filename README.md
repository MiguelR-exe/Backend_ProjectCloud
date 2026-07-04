# Backend — Sistema de Gestión de Pedidos (Madam Tusan)

Backend serverless en AWS con 3 microservicios (catalog, orders, workflow),
arquitectura basada en eventos y flujo de trabajo con Step Functions
(patrón Wait for Callback with Task Token).

Se despliega completo con un solo comando usando Serverless Framework.

## Qué incluye

- 3 tablas DynamoDB: Orders, Products, Workflow
- 9 Lambdas (en la carpeta `handlers/`)
- API Gateway con todas las rutas REST
- EventBridge (dispara el workflow al crear un pedido)
- Step Functions (flujo del pedido con Wait for Callback, Choice y manejo de errores)

## Requisitos previos

- Node.js 18 o superior
- Serverless Framework v3:  `npm install -g serverless`
- Cuenta de AWS Academy (Learner Lab) con el rol LabRole

## Pasos para desplegar

1. Clona el repositorio y entra a la carpeta:
   ```bash
   git clone <URL-DEL-REPO>
   cd madamtusan-backend
   ```

2. Instala el plugin de Step Functions:
   ```bash
   npm install
   ```

3. Conecta tus credenciales de AWS Academy:
   - Inicia el Learner Lab y abre "AWS Details"
   - Copia el bloque de credenciales (incluye aws_session_token)
   - Pégalo en el archivo ~/.aws/credentials

4. Despliega todo:
   ```bash
   serverless deploy
   ```

5. Al terminar, copia las URLs de API Gateway que aparecen al final.

## QUÉ DEBES CAMBIAR (importante)

Antes o después de desplegar, revisa estos puntos:

1. **URL de OCI (Rappi)** — en `serverless.yml`, variable `OCI_API2_URL`.
   Reemplaza el placeholder por la URL real de la API #2 de OCI cuando esté lista.
   Luego vuelve a ejecutar `serverless deploy`.

2. **Región** — por defecto es `us-east-1` (la de Academy). Solo cámbiala
   si tu cuenta usa otra región.

3. **Credenciales** — cada vez que se reinicia el Learner Lab, las credenciales
   cambian. Vuelve a copiarlas a ~/.aws/credentials antes de desplegar.

4. **Frontends** — después del deploy, pega la URL de API Gateway en el
   archivo de configuración de cada frontend (web-cliente y web-trabajadores).

## Probar que funciona

Crear un pedido (reemplaza con tu URL de API Gateway):
```bash
curl -X POST https://TU-URL/dev/orders \
  -H "Content-Type: application/json" \
  -d '{"cliente":"Juan","items":["Chaufa"]}'
```

Listar pedidos:
```bash
curl https://TU-URL/dev/orders
```

## Eliminar todo lo desplegado

```bash
serverless remove
```

## Estructura del proyecto

```
madamtusan-backend/
├── serverless.yml       # toda la infraestructura
├── package.json         # plugin de step functions
├── .gitignore
└── handlers/            # las 9 lambdas
    ├── listProducts.py
    ├── getProduct.py
    ├── createOrder.py
    ├── getOrder.py
    ├── listOrders.py
    ├── startWorkflow.py
    ├── registrarPaso.py
    ├── completeStep.py
    └── callRappi.py
```
