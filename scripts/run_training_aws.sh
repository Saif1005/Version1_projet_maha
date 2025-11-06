#!/bin/bash
# Script pour lancer l'entraînement sur AWS ECS
# Usage: ./scripts/run_training_aws.sh [num_rounds]

set -e

NUM_ROUNDS=${1:-10}
PROJECT_NAME="fl-crew-reddit"
AWS_REGION=${AWS_REGION:-us-east-1}

echo "=========================================="
echo "🏋️  Lancement de l'entraînement sur AWS"
echo "=========================================="
echo "Nombre de rounds: $NUM_ROUNDS"
echo "=========================================="
echo ""

# Récupérer le cluster ECS depuis Terraform
cd terraform
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name 2>/dev/null || echo "${PROJECT_NAME}-cluster")
cd ..

# Récupérer la task definition
TASK_DEFINITION=$(aws ecs list-task-definitions \
    --family-prefix "${PROJECT_NAME}-task" \
    --region $AWS_REGION \
    --query 'taskDefinitionArns[-1]' \
    --output text)

if [ -z "$TASK_DEFINITION" ] || [ "$TASK_DEFINITION" == "None" ]; then
    echo "❌ Task definition non trouvée"
    exit 1
fi

# Récupérer le subnet et security group depuis Terraform
cd terraform
SUBNET_ID=$(terraform output -raw subnet_id 2>/dev/null || echo "")
SECURITY_GROUP=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=${PROJECT_NAME}-sg" \
    --region $AWS_REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "")
cd ..

# Lancer la tâche ECS
echo "🚀 Lancement de la tâche d'entraînement..."

RUN_TASK_CMD="aws ecs run-task \
    --cluster $ECS_CLUSTER \
    --task-definition $TASK_DEFINITION \
    --launch-type FARGATE \
    --region $AWS_REGION \
    --overrides '{
        \"containerOverrides\": [{
            \"name\": \"${PROJECT_NAME}-container\",
            \"command\": [\"python\", \"-m\", \"fl_crew_reddit.main\"],
            \"environment\": [
                {\"name\": \"FEDERATION_ROUNDS\", \"value\": \"$NUM_ROUNDS\"},
                {\"name\": \"USE_S3_STORAGE\", \"value\": \"true\"}
            ]
        }]
    }'"

if [ -n "$SUBNET_ID" ]; then
    RUN_TASK_CMD="$RUN_TASK_CMD --network-configuration 'awsvpcConfiguration={subnets=[$SUBNET_ID]"
    if [ -n "$SECURITY_GROUP" ]; then
        RUN_TASK_CMD="$RUN_TASK_CMD,securityGroups=[$SECURITY_GROUP]"
    fi
    RUN_TASK_CMD="$RUN_TASK_CMD,assignPublicIp=ENABLED}'"
fi

TASK_ARN=$(eval $RUN_TASK_CMD | jq -r '.tasks[0].taskArn')

if [ -z "$TASK_ARN" ] || [ "$TASK_ARN" == "null" ]; then
    echo "❌ Erreur lors du lancement de la tâche"
    exit 1
fi

echo "✅ Tâche lancée: $TASK_ARN"
echo ""
echo "📊 Suivre les logs avec:"
echo "aws logs tail /ecs/${PROJECT_NAME} --follow --region $AWS_REGION"
echo ""
echo "Ou dans la console AWS:"
echo "https://${AWS_REGION}.console.aws.amazon.com/ecs/v2/clusters/$ECS_CLUSTER/tasks"

