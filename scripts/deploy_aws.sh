#!/bin/bash
# Script de déploiement AWS pour FL Crew Reddit
# Usage: ./scripts/deploy_aws.sh [environment]

set -e

ENVIRONMENT=${1:-prod}
AWS_REGION=${AWS_REGION:-us-east-1}
PROJECT_NAME="fl-crew-reddit"
S3_BUCKET_NAME="${PROJECT_NAME}-${ENVIRONMENT}-$(date +%s)"

echo "=========================================="
echo " Déploiement FL Crew Reddit sur AWS"
echo "=========================================="
echo "Environnement: $ENVIRONMENT"
echo "Région: $AWS_REGION"
echo "Bucket S3: $S3_BUCKET_NAME"
echo "=========================================="
echo ""

# Vérifier que AWS CLI est installé
if ! command -v aws &> /dev/null; then
    echo " AWS CLI n'est pas installé"
    exit 1
fi

# Vérifier les credentials AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo " Credentials AWS non configurés"
    exit 1
fi

echo " Credentials AWS vérifiés"

# 1. Créer le bucket S3 pour Terraform state (si nécessaire)
TERRAFORM_STATE_BUCKET="${PROJECT_NAME}-terraform-state-${ENVIRONMENT}"
if ! aws s3 ls "s3://${TERRAFORM_STATE_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    echo " Création du bucket S3 pour Terraform state..."
    aws s3 mb "s3://${TERRAFORM_STATE_BUCKET}" --region $AWS_REGION
    aws s3api put-bucket-versioning \
        --bucket "${TERRAFORM_STATE_BUCKET}" \
        --versioning-configuration Status=Enabled
fi

# 2. Build et push de l'image Docker vers ECR
echo ""
echo " Build et push de l'image Docker..."

# Obtenir l'URL du repository ECR (créé par Terraform)
ECR_REPO=$(aws ecr describe-repositories --repository-names $PROJECT_NAME --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text 2>/dev/null || echo "")

if [ -z "$ECR_REPO" ]; then
    echo "  Repository ECR n'existe pas encore. Il sera créé par Terraform."
    ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}"
fi

# Login à ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

# Build l'image
echo " Build de l'image Docker..."
docker build -t ${PROJECT_NAME}:latest .

# Tag et push
docker tag ${PROJECT_NAME}:latest ${ECR_REPO}:latest
docker tag ${PROJECT_NAME}:latest ${ECR_REPO}:$(git rev-parse --short HEAD 2>/dev/null || echo "latest")

echo " Push de l'image vers ECR..."
docker push ${ECR_REPO}:latest
docker push ${ECR_REPO}:$(git rev-parse --short HEAD 2>/dev/null || echo "latest")

# 3. Déployer l'infrastructure avec Terraform
echo ""
echo "  Déploiement de l'infrastructure avec Terraform..."

cd terraform

# Initialiser Terraform
terraform init \
    -backend-config="bucket=${TERRAFORM_STATE_BUCKET}" \
    -backend-config="key=fl-crew-reddit/terraform.tfstate" \
    -backend-config="region=${AWS_REGION}"

# Plan
terraform plan \
    -var="aws_region=${AWS_REGION}" \
    -var="environment=${ENVIRONMENT}" \
    -var="s3_bucket_name=${S3_BUCKET_NAME}" \
    -out=tfplan

# Apply
echo ""
read -p "Appliquer les changements Terraform? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply tfplan
else
    echo " Déploiement annulé"
    exit 1
fi

# Récupérer les outputs
ECR_REPO_URL=$(terraform output -raw ecr_repository_url)
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)

cd ..

# 4. Mettre à jour les secrets AWS Secrets Manager
echo ""
echo " Configuration des secrets AWS..."

# OpenAI API Key
if [ -n "$OPENAI_API_KEY" ]; then
    aws secretsmanager put-secret-value \
        --secret-id "${PROJECT_NAME}/openai-api-key" \
        --secret-string "$OPENAI_API_KEY" \
        --region $AWS_REGION || \
    aws secretsmanager create-secret \
        --name "${PROJECT_NAME}/openai-api-key" \
        --secret-string "$OPENAI_API_KEY" \
        --region $AWS_REGION
    echo " OpenAI API Key configuré"
fi

# Reddit Client ID
if [ -n "$REDDIT_CLIENT_ID" ]; then
    aws secretsmanager put-secret-value \
        --secret-id "${PROJECT_NAME}/reddit-client-id" \
        --secret-string "$REDDIT_CLIENT_ID" \
        --region $AWS_REGION || \
    aws secretsmanager create-secret \
        --name "${PROJECT_NAME}/reddit-client-id" \
        --secret-string "$REDDIT_CLIENT_ID" \
        --region $AWS_REGION
    echo " Reddit Client ID configuré"
fi

# Reddit Client Secret
if [ -n "$REDDIT_CLIENT_SECRET" ]; then
    aws secretsmanager put-secret-value \
        --secret-id "${PROJECT_NAME}/reddit-client-secret" \
        --secret-string "$REDDIT_CLIENT_SECRET" \
        --region $AWS_REGION || \
    aws secretsmanager create-secret \
        --name "${PROJECT_NAME}/reddit-client-secret" \
        --secret-string "$REDDIT_CLIENT_SECRET" \
        --region $AWS_REGION
    echo " Reddit Client Secret configuré"
fi

# 5. Mettre à jour la task definition ECS avec la nouvelle image
echo ""
echo " Mise à jour du service ECS..."

aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service "${PROJECT_NAME}-service" \
    --force-new-deployment \
    --region $AWS_REGION || echo "  Service ECS non trouvé. Créez-le manuellement."

echo ""
echo "=========================================="
echo " Déploiement terminé!"
echo "=========================================="
echo "ECR Repository: $ECR_REPO_URL"
echo "ECS Cluster: $ECS_CLUSTER"
echo "S3 Bucket: $S3_BUCKET_NAME"
echo "=========================================="

