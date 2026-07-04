# Backend completo — Madam Tusan

Despliega TODO el backend con un comando: 3 tablas DynamoDB, 8 Lambdas,
API Gateway, EventBridge y la Step Function con Wait-for-Callback.

## Estructura
```
backend-completo/
├── serverless.yml          # toda la infraestructura
├── package.json            # plugin de step functions
└── handlers/
    ├── catalog.py          # listProducts, getProduct
    ├── orders.py           # createOrder, getOrder, listOrders
    └── workflow.py         # startWorkflow, registrarPaso, completeStep, callRappi
```

## Requisitos
- Node.js 18+ y Serverless Framework v3: `npm install -g serverless`
- Credenciales de AWS Academy en ~/.aws/credentials (con aws_session_token)

## Desplegar en la nueva cuenta

1. Copia las credenciales del Learner Lab (AWS Details) a ~/.aws/credentials
2. Instala el plugin de Step Functions:
   ```bash
   npm install
   ```
3. Despliega todo:
   ```bash
   serverless deploy
   ```
4. Al terminar, verás las URLs de API Gateway (endpoints) al final.

## Notas Academy
- Usa LabRole automáticamente (ya configurado en el yml).
- Región us-east-1.
- Si el lab se reinicia, recopia las credenciales y vuelve a desplegar.

## Después del deploy
- Pega la URL de API Gateway en tus frontends (config.js).
- Cuando tengas la URL de OCI API #2, cámbiala en serverless.yml
  (variable OCI_API2_URL) y vuelve a hacer serverless deploy.

## Eliminar todo
```bash
serverless remove
```
