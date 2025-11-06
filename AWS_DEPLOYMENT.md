# Guide de Déploiement AWS - FL Crew Reddit

Ce guide explique comment déployer le système FL Crew Reddit sur AWS pour l'entraînement et l'exécution sur les serveurs AWS.

## Architecture AWS

Le déploiement utilise:
- **S3** : Stockage des données et modèles
- **ECR** : Registry Docker pour les images
- **ECS Fargate** : Exécution des conteneurs (avec support GPU)
- **Secrets Manager** : Gestion des credentials
- **CloudWatch** : Logs et monitoring
- **Terraform** : Infrastructure as Code

## Prérequis

1. **AWS CLI** installé et configuré
2. **Docker** installé
3. **Terraform** >= 1.0 installé
4. **Credentials AWS** avec permissions appropriées
5. **jq** pour le parsing JSON (optionnel)

## Configuration Initiale

### 1. Variables d'environnement

Créez un fichier `.env` ou configurez les variables d'environnement:

```bash
# AWS Configuration
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
export AWS_S3_BUCKET="fl-crew-reddit-prod-1234567890"
export USE_S3_STORAGE="true"

# API Keys
export OPENAI_API_KEY="your-openai-key"
export REDDIT_CLIENT_ID="your-reddit-client-id"
export REDDIT_CLIENT_SECRET="your-reddit-secret"

# Configuration LLM
export BASE_LLM_MODEL="mistralai/Mistral-7B-v0.1"
export AGENT_LLM_MODEL="gpt-4"
```

### 2. Configuration Terraform

Éditez `terraform/variables.tf` pour personnaliser:
- Région AWS
- Type d'instance
- Nom du bucket S3 (doit être unique globalement)

## Déploiement

### Option 1: Script Automatique

```bash
# Rendre le script exécutable
chmod +x scripts/deploy_aws.sh

# Déployer
./scripts/deploy_aws.sh prod
```

### Option 2: Déploiement Manuel

#### Étape 1: Créer l'infrastructure avec Terraform

```bash
cd terraform

# Initialiser Terraform
terraform init

# Planifier les changements
terraform plan \
    -var="s3_bucket_name=fl-crew-reddit-prod-$(date +%s)" \
    -var="aws_region=us-east-1"

# Appliquer
terraform apply
```

#### Étape 2: Build et Push de l'image Docker

```bash
# Login à ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    $(aws ecr describe-repositories --repository-names fl-crew-reddit --query 'repositories[0].repositoryUri' --output text)

# Build
docker build -t fl-crew-reddit:latest .

# Tag et push
ECR_REPO=$(terraform output -raw ecr_repository_url)
docker tag fl-crew-reddit:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest
```

#### Étape 3: Configurer les Secrets

```bash
# OpenAI API Key
aws secretsmanager create-secret \
    --name "fl-crew-reddit/openai-api-key" \
    --secret-string "your-openai-key" \
    --region us-east-1

# Reddit Credentials
aws secretsmanager create-secret \
    --name "fl-crew-reddit/reddit-client-id" \
    --secret-string "your-reddit-client-id" \
    --region us-east-1

aws secretsmanager create-secret \
    --name "fl-crew-reddit/reddit-client-secret" \
    --secret-string "your-reddit-secret" \
    --region us-east-1
```

## Lancer l'Entraînement

### Option 1: Script Automatique

```bash
chmod +x scripts/run_training_aws.sh
./scripts/run_training_aws.sh 10  # 10 rounds
```

### Option 2: Lancer une tâche ECS manuellement

```bash
# Récupérer les informations nécessaires
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)
TASK_DEF=$(aws ecs list-task-definitions \
    --family-prefix fl-crew-reddit-task \
    --query 'taskDefinitionArns[-1]' \
    --output text)

# Lancer la tâche
aws ecs run-task \
    --cluster $ECS_CLUSTER \
    --task-definition $TASK_DEF \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],assignPublicIp=ENABLED}" \
    --overrides '{
        "containerOverrides": [{
            "name": "fl-crew-reddit-container",
            "command": ["python", "-m", "fl_crew_reddit.main"],
            "environment": [
                {"name": "FEDERATION_ROUNDS", "value": "10"},
                {"name": "USE_S3_STORAGE", "value": "true"}
            ]
        }]
    }'
```

## Monitoring

### Voir les logs

```bash
# Via AWS CLI
aws logs tail /ecs/fl-crew-reddit --follow --region us-east-1

# Via Console AWS
# https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups
```

### Voir les tâches ECS

```bash
# Lister les tâches
aws ecs list-tasks --cluster fl-crew-reddit-cluster --region us-east-1

# Détails d'une tâche
aws ecs describe-tasks \
    --cluster fl-crew-reddit-cluster \
    --tasks <task-arn> \
    --region us-east-1
```

## Stockage S3

Les données et modèles sont automatiquement sauvegardés dans S3:

- **Données**: `s3://<bucket>/fl_crew_reddit/data/`
- **Modèles**: `s3://<bucket>/fl_crew_reddit/models/`
- **Logs**: `s3://<bucket>/fl_crew_reddit/logs/`
- **Résultats**: `s3://<bucket>/fl_crew_reddit/results/`

### Synchroniser depuis S3

```bash
# Télécharger les modèles
aws s3 sync s3://<bucket>/fl_crew_reddit/models/ ./models/

# Télécharger les résultats
aws s3 sync s3://<bucket>/fl_crew_reddit/results/ ./results/
```

## Coûts Estimés

- **ECS Fargate (GPU)**: ~$0.50-1.00/heure selon l'instance
- **S3 Storage**: ~$0.023/GB/mois
- **ECR**: ~$0.10/GB/mois
- **CloudWatch Logs**: ~$0.50/GB
- **Secrets Manager**: ~$0.40/secret/mois

## Dépannage

### Problème: Tâche ECS ne démarre pas

```bash
# Vérifier les événements
aws ecs describe-tasks \
    --cluster <cluster-name> \
    --tasks <task-arn> \
    --region us-east-1 | jq '.tasks[0].stoppedReason'
```

### Problème: Erreur de permissions S3

Vérifiez que le rôle IAM `fl-crew-reddit-ecs-task-role` a les permissions S3 nécessaires.

### Problème: Image Docker trop grande

Optimisez le Dockerfile ou utilisez des images multi-stage.

## Nettoyage

Pour supprimer toutes les ressources:

```bash
cd terraform
terraform destroy
```

**Attention**: Cela supprimera toutes les données dans S3 si configuré ainsi.

## Support GPU

Pour utiliser des GPU sur ECS, vous devez:
1. Utiliser des instances avec GPU (g4dn.xlarge, p3.2xlarge, etc.)
2. Configurer la task definition avec `gpu` dans containerDefinitions
3. Utiliser ECS avec EC2 (pas Fargate) pour GPU, ou ECS Fargate avec GPU support

## Références

- [Documentation ECS](https://docs.aws.amazon.com/ecs/)
- [Documentation S3](https://docs.aws.amazon.com/s3/)
- [Documentation Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

