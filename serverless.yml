service: madamtusan-backend

frameworkVersion: "3"

provider:
  name: aws
  runtime: python3.12
  region: us-east-1
  stage: dev
  # --- AWS ACADEMY: usar el rol predefinido LabRole ---
  iam:
    role: arn:aws:iam::${aws:accountId}:role/LabRole
  environment:
    ORDERS_TABLE: ms-orders-orders-${self:provider.stage}
    PRODUCTS_TABLE: ms-catalog-products-${self:provider.stage}
    WORKFLOW_TABLE: ms-workflow-${self:provider.stage}
    STATE_MACHINE_ARN: ${self:resources.Outputs.StateMachineArn.Value}
    OCI_API2_URL: "https://TU-OCI-API2/estado"

plugins:
  - serverless-step-functions

package:
  patterns:
    - "!node_modules/**"
    - "!package*.json"

functions:
  # ---------- ms-catalog ----------
  listProducts:
    handler: handlers/listProducts.lambda_handler
    events:
      - http: { path: products, method: get, cors: true }
  getProduct:
    handler: handlers/getProduct.lambda_handler
    events:
      - http: { path: products/{id}, method: get, cors: true }

  # ---------- ms-orders ----------
  createOrder:
    handler: handlers/createOrder.lambda_handler
    events:
      - http: { path: orders, method: post, cors: true }
  getOrder:
    handler: handlers/getOrder.lambda_handler
    events:
      - http: { path: orders/{id}, method: get, cors: true }
  listOrders:
    handler: handlers/listOrders.lambda_handler
    events:
      - http: { path: orders, method: get, cors: true }

  # ---------- ms-workflow ----------
  startWorkflow:
    handler: handlers/startWorkflow.lambda_handler
    events:
      - eventBridge:
          pattern:
            source:
              - madamtusan.orders
            detail-type:
              - PedidoCreado
  registrarPaso:
    handler: handlers/registrarPaso.lambda_handler
  completeStep:
    handler: handlers/completeStep.lambda_handler
    events:
      - http: { path: orders/{id}/complete, method: post, cors: true }
  callRappi:
    handler: handlers/callRappi.lambda_handler

stepFunctions:
  stateMachines:
    workflowPedidos:
      name: workflow-pedidos-${self:provider.stage}
      role: arn:aws:iam::${aws:accountId}:role/LabRole
      definition:
        Comment: "Flujo de pedidos Madam Tusan - Wait for Callback + Choice + Retry/Catch"
        StartAt: Cocinar
        States:
          Cocinar:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke.waitForTaskToken
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-registrarPaso
              Payload:
                order_id.$: "$.order_id"
                tenant_id.$: "$.tenant_id"
                origen.$: "$.origen"
                paso: COCINANDO
                rol: cocinero
                taskToken.$: "$$.Task.Token"
            TimeoutSeconds: 3600
            ResultPath: "$.resultadoCocina"
            Retry:
              - ErrorEquals: ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException", "Lambda.TooManyRequestsException"]
                IntervalSeconds: 2
                MaxAttempts: 3
                BackoffRate: 2.0
            Catch:
              - ErrorEquals: ["States.Timeout"]
                ResultPath: "$.error"
                Next: PedidoVencido
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: PedidoFallido
            Next: EsRappiCocina
          EsRappiCocina:
            Type: Choice
            Choices:
              - Variable: "$.origen"
                StringEquals: rappi
                Next: NotificarCocina
            Default: Empacar
          NotificarCocina:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-callRappi
              Payload:
                order_id.$: "$.order_id"
                origen.$: "$.origen"
                paso: COCINANDO
            ResultPath: "$.notifCocina"
            Catch:
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: Empacar
            Next: Empacar
          Empacar:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke.waitForTaskToken
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-registrarPaso
              Payload:
                order_id.$: "$.order_id"
                tenant_id.$: "$.tenant_id"
                origen.$: "$.origen"
                paso: EMPACANDO
                rol: despachador
                taskToken.$: "$$.Task.Token"
            TimeoutSeconds: 3600
            ResultPath: "$.resultadoEmpaque"
            Retry:
              - ErrorEquals: ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException", "Lambda.TooManyRequestsException"]
                IntervalSeconds: 2
                MaxAttempts: 3
                BackoffRate: 2.0
            Catch:
              - ErrorEquals: ["States.Timeout"]
                ResultPath: "$.error"
                Next: PedidoVencido
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: PedidoFallido
            Next: EsRappiEmpaque
          EsRappiEmpaque:
            Type: Choice
            Choices:
              - Variable: "$.origen"
                StringEquals: rappi
                Next: NotificarEmpaque
            Default: Repartir
          NotificarEmpaque:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-callRappi
              Payload:
                order_id.$: "$.order_id"
                origen.$: "$.origen"
                paso: EMPACANDO
            ResultPath: "$.notifEmpaque"
            Catch:
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: Repartir
            Next: Repartir
          Repartir:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke.waitForTaskToken
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-registrarPaso
              Payload:
                order_id.$: "$.order_id"
                tenant_id.$: "$.tenant_id"
                origen.$: "$.origen"
                paso: EN_REPARTO
                rol: repartidor
                taskToken.$: "$$.Task.Token"
            TimeoutSeconds: 3600
            ResultPath: "$.resultadoReparto"
            Retry:
              - ErrorEquals: ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException", "Lambda.TooManyRequestsException"]
                IntervalSeconds: 2
                MaxAttempts: 3
                BackoffRate: 2.0
            Catch:
              - ErrorEquals: ["States.Timeout"]
                ResultPath: "$.error"
                Next: PedidoVencido
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: PedidoFallido
            Next: EsRappiReparto
          EsRappiReparto:
            Type: Choice
            Choices:
              - Variable: "$.origen"
                StringEquals: rappi
                Next: NotificarReparto
            Default: Entregar
          NotificarReparto:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-callRappi
              Payload:
                order_id.$: "$.order_id"
                origen.$: "$.origen"
                paso: EN_REPARTO
            ResultPath: "$.notifReparto"
            Catch:
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: Entregar
            Next: Entregar
          Entregar:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke.waitForTaskToken
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-registrarPaso
              Payload:
                order_id.$: "$.order_id"
                tenant_id.$: "$.tenant_id"
                origen.$: "$.origen"
                paso: ENTREGADO
                rol: cliente
                taskToken.$: "$$.Task.Token"
            TimeoutSeconds: 3600
            ResultPath: "$.resultadoEntrega"
            Retry:
              - ErrorEquals: ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException", "Lambda.TooManyRequestsException"]
                IntervalSeconds: 2
                MaxAttempts: 3
                BackoffRate: 2.0
            Catch:
              - ErrorEquals: ["States.Timeout"]
                ResultPath: "$.error"
                Next: PedidoVencido
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: PedidoFallido
            Next: EsRappiEntrega
          EsRappiEntrega:
            Type: Choice
            Choices:
              - Variable: "$.origen"
                StringEquals: rappi
                Next: NotificarEntrega
            Default: Finalizar
          NotificarEntrega:
            Type: Task
            Resource: arn:aws:states:::lambda:invoke
            Parameters:
              FunctionName: ${self:service}-${self:provider.stage}-callRappi
              Payload:
                order_id.$: "$.order_id"
                origen.$: "$.origen"
                paso: ENTREGADO
            ResultPath: "$.notifEntrega"
            Catch:
              - ErrorEquals: ["States.ALL"]
                ResultPath: "$.error"
                Next: Finalizar
            Next: Finalizar
          Finalizar:
            Type: Succeed
          PedidoVencido:
            Type: Fail
            Error: PedidoVencido
            Cause: "Nadie atendio un paso a tiempo"
          PedidoFallido:
            Type: Fail
            Error: PedidoFallido
            Cause: "Error inesperado en el flujo"

resources:
  Resources:
    OrdersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:provider.environment.ORDERS_TABLE}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - { AttributeName: tenant_id, AttributeType: S }
          - { AttributeName: order_id, AttributeType: S }
        KeySchema:
          - { AttributeName: tenant_id, KeyType: HASH }
          - { AttributeName: order_id, KeyType: RANGE }
    ProductsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:provider.environment.PRODUCTS_TABLE}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - { AttributeName: product_id, AttributeType: S }
        KeySchema:
          - { AttributeName: product_id, KeyType: HASH }
    WorkflowTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:provider.environment.WORKFLOW_TABLE}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - { AttributeName: order_id, AttributeType: S }
          - { AttributeName: tenant_id, AttributeType: S }
        KeySchema:
          - { AttributeName: order_id, KeyType: HASH }
          - { AttributeName: tenant_id, KeyType: RANGE }

  Outputs:
    StateMachineArn:
      Description: ARN de la state machine
      Value:
        Ref: WorkflowPedidosStepFunctionsStateMachine
