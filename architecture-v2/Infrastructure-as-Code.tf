# SuperSmartMatch V2 - Infrastructure as Code (Terraform)

## 🏗️ Architecture Infrastructure Overview

Cette infrastructure Terraform déploie l'architecture complète SuperSmartMatch V2 sur AWS avec :
- **Multi-AZ** : Haute disponibilité
- **Auto-scaling** : Scaling automatique basé sur la charge
- **Security** : WAF, encryption, network isolation
- **Monitoring** : Observabilité complète
- **CI/CD** : Pipeline automatisé

### 📁 Structure du Projet

```
terraform/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── modules/
│   ├── networking/
│   ├── security/
│   ├── eks/
│   ├── databases/
│   ├── monitoring/
│   └── cdn/
├── shared/
│   ├── variables.tf
│   ├── outputs.tf
│   └── versions.tf
└── scripts/
    ├── deploy.sh
    └── destroy.sh
```

---

## 1. 🌐 Configuration Principale

### Main Configuration (main.tf)

```hcl
# ================================
# SUPERSMARTMATCH V2 - MAIN CONFIGURATION
# ================================

terraform {
  required_version = ">= 1.6"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  
  backend "s3" {
    bucket         = "supersmartmatch-terraform-state"
    key            = "v2/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "supersmartmatch-terraform-locks"
  }
}

# ================================
# PROVIDERS CONFIGURATION
# ================================

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "SuperSmartMatch-V2"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner_team
      CostCenter  = var.cost_center
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# ================================
# LOCAL VALUES
# ================================

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner_team
    CostCenter  = var.cost_center
  }
  
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 3)
}

# ================================
# DATA SOURCES
# ================================

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# ================================
# RANDOM RESOURCES
# ================================

resource "random_password" "database_passwords" {
  for_each = toset(["postgres", "redis", "clickhouse"])
  
  length  = 32
  special = true
}

resource "random_id" "cluster_suffix" {
  byte_length = 4
}

# ================================
# NETWORKING MODULE
# ================================

module "networking" {
  source = "./modules/networking"
  
  name_prefix        = local.name_prefix
  availability_zones = local.availability_zones
  
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  database_subnet_cidrs = var.database_subnet_cidrs
  
  enable_nat_gateway     = true
  enable_vpn_gateway     = var.enable_vpn_gateway
  enable_dns_hostnames   = true
  enable_dns_support     = true
  enable_flow_logs       = true
  
  tags = local.common_tags
}

# ================================
# SECURITY MODULE
# ================================

module "security" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  vpc_id      = module.networking.vpc_id
  
  # WAF Configuration
  enable_waf                = true
  waf_rate_limit           = var.waf_rate_limit
  allowed_countries        = var.allowed_countries
  blocked_ips              = var.blocked_ips
  
  # Certificate Management
  domain_name              = var.domain_name
  certificate_arn          = var.certificate_arn
  
  # KMS Configuration
  enable_kms               = true
  kms_deletion_window      = var.kms_deletion_window
  
  tags = local.common_tags
}

# ================================
# EKS CLUSTER MODULE
# ================================

module "eks" {
  source = "./modules/eks"
  
  cluster_name    = "${local.name_prefix}-cluster-${random_id.cluster_suffix.hex}"
  cluster_version = var.kubernetes_version
  
  vpc_id          = module.networking.vpc_id
  subnet_ids      = module.networking.private_subnet_ids
  
  # Node Groups Configuration
  node_groups = {
    general = {
      desired_capacity = var.eks_node_groups.general.desired_capacity
      max_capacity     = var.eks_node_groups.general.max_capacity
      min_capacity     = var.eks_node_groups.general.min_capacity
      instance_types   = var.eks_node_groups.general.instance_types
      
      k8s_labels = {
        role = "general"
      }
      
      taints = []
    }
    
    compute_intensive = {
      desired_capacity = var.eks_node_groups.compute_intensive.desired_capacity
      max_capacity     = var.eks_node_groups.compute_intensive.max_capacity
      min_capacity     = var.eks_node_groups.compute_intensive.min_capacity
      instance_types   = var.eks_node_groups.compute_intensive.instance_types
      
      k8s_labels = {
        role = "compute"
      }
      
      taints = [{
        key    = "compute-intensive"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
    
    ml_workloads = {
      desired_capacity = var.eks_node_groups.ml_workloads.desired_capacity
      max_capacity     = var.eks_node_groups.ml_workloads.max_capacity
      min_capacity     = var.eks_node_groups.ml_workloads.min_capacity
      instance_types   = var.eks_node_groups.ml_workloads.instance_types
      
      k8s_labels = {
        role = "ml"
      }
      
      taints = [{
        key    = "ml-workloads"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }
  
  # Cluster Add-ons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
  
  # Security Configuration
  cluster_encryption_config = [{
    provider_key_arn = module.security.kms_key_arn
    resources        = ["secrets"]
  }]
  
  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = var.cluster_endpoint_public_access
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
  
  # Logging
  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  
  tags = local.common_tags
}

# ================================
# DATABASES MODULE
# ================================

module "databases" {
  source = "./modules/databases"
  
  name_prefix = local.name_prefix
  vpc_id      = module.networking.vpc_id
  subnet_ids  = module.networking.database_subnet_ids
  
  # PostgreSQL Configuration
  postgres_config = {
    engine_version          = var.postgres_engine_version
    instance_class          = var.postgres_instance_class
    allocated_storage       = var.postgres_allocated_storage
    max_allocated_storage   = var.postgres_max_allocated_storage
    storage_encrypted       = true
    kms_key_id             = module.security.kms_key_arn
    
    multi_az               = var.environment == "prod" ? true : false
    backup_retention_period = var.postgres_backup_retention
    backup_window          = "03:00-04:00"
    maintenance_window     = "sun:04:00-sun:05:00"
    
    performance_insights_enabled = true
    monitoring_interval         = 60
    
    database_name = "supersmartmatch_core"
    username      = "supersmartmatch_admin"
    password      = random_password.database_passwords["postgres"].result
  }
  
  # Redis Configuration
  redis_config = {
    node_type                  = var.redis_node_type
    num_cache_nodes           = var.redis_num_nodes
    parameter_group_name      = var.redis_parameter_group
    port                      = 6379
    engine_version            = var.redis_engine_version
    
    at_rest_encryption_enabled = true
    transit_encryption_enabled  = true
    auth_token                 = random_password.database_passwords["redis"].result
    
    automatic_failover_enabled = var.environment == "prod" ? true : false
    multi_az_enabled          = var.environment == "prod" ? true : false
    
    snapshot_retention_limit = var.redis_backup_retention
    snapshot_window         = "03:00-05:00"
    maintenance_window      = "sun:05:00-sun:07:00"
  }
  
  # ClickHouse Configuration (using EC2 instances)
  clickhouse_config = {
    instance_type     = var.clickhouse_instance_type
    instance_count    = var.clickhouse_instance_count
    volume_size       = var.clickhouse_volume_size
    volume_type       = "gp3"
    volume_encrypted  = true
    kms_key_id        = module.security.kms_key_arn
  }
  
  # TimeScaleDB Configuration (PostgreSQL extension)
  timescaledb_config = {
    engine_version        = var.timescaledb_engine_version
    instance_class        = var.timescaledb_instance_class
    allocated_storage     = var.timescaledb_allocated_storage
    storage_encrypted     = true
    kms_key_id           = module.security.kms_key_arn
    
    database_name = "supersmartmatch_temporal"
    username      = "timescale_admin"
    password      = random_password.database_passwords["timescale"].result
  }
  
  tags = local.common_tags
}

# ================================
# MONITORING MODULE
# ================================

module "monitoring" {
  source = "./modules/monitoring"
  
  name_prefix    = local.name_prefix
  cluster_name   = module.eks.cluster_name
  vpc_id         = module.networking.vpc_id
  
  # Prometheus Configuration
  prometheus_config = {
    storage_class     = "gp2"
    storage_size      = var.prometheus_storage_size
    retention_period  = var.prometheus_retention_period
    replica_count     = var.environment == "prod" ? 2 : 1
  }
  
  # Grafana Configuration
  grafana_config = {
    admin_password    = var.grafana_admin_password
    storage_size      = var.grafana_storage_size
    ingress_enabled   = true
    ingress_host      = "grafana.${var.domain_name}"
  }
  
  # Jaeger Configuration
  jaeger_config = {
    storage_type     = "elasticsearch"
    storage_size     = var.jaeger_storage_size
    retention_days   = var.jaeger_retention_days
  }
  
  # ELK Stack Configuration
  elk_config = {
    elasticsearch_nodes    = var.elk_elasticsearch_nodes
    elasticsearch_storage  = var.elk_elasticsearch_storage
    kibana_enabled        = true
    logstash_enabled      = true
  }
  
  # AlertManager Configuration
  alertmanager_config = {
    slack_webhook_url     = var.slack_webhook_url
    pagerduty_service_key = var.pagerduty_service_key
    email_smtp_host       = var.email_smtp_host
    email_from            = var.email_from
  }
  
  tags = local.common_tags
}

# ================================
# CDN & LOAD BALANCER MODULE
# ================================

module "cdn" {
  source = "./modules/cdn"
  
  name_prefix = local.name_prefix
  
  # CloudFront Configuration
  domain_name        = var.domain_name
  certificate_arn    = var.certificate_arn
  
  # Origins Configuration
  origins = [
    {
      domain_name = module.eks.cluster_endpoint
      origin_id   = "api-gateway"
      custom_origin_config = {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
      }
    }
  ]
  
  # Cache Behaviors
  default_cache_behavior = {
    target_origin_id       = "api-gateway"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods  = ["GET", "HEAD"]
    
    forwarded_values = {
      query_string = true
      headers      = ["Authorization", "Content-Type"]
      cookies = {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }
  
  # WAF Association
  web_acl_id = module.security.waf_web_acl_arn
  
  # Geographic Restrictions
  geo_restriction = {
    restriction_type = "whitelist"
    locations        = var.allowed_countries
  }
  
  tags = local.common_tags
}

# ================================
# APPLICATION DEPLOYMENT
# ================================

resource "helm_release" "supersmartmatch_v2" {
  depends_on = [module.eks]
  
  name       = "supersmartmatch-v2"
  namespace  = "supersmartmatch"
  create_namespace = true
  
  chart      = "../helm-charts/supersmartmatch-v2"
  
  values = [
    yamlencode({
      global = {
        environment = var.environment
        domain      = var.domain_name
        
        database = {
          postgres = {
            host     = module.databases.postgres_endpoint
            port     = module.databases.postgres_port
            database = "supersmartmatch_core"
            username = "supersmartmatch_admin"
            password = random_password.database_passwords["postgres"].result
          }
          
          redis = {
            host     = module.databases.redis_endpoint
            port     = 6379
            password = random_password.database_passwords["redis"].result
          }
          
          clickhouse = {
            hosts = module.databases.clickhouse_endpoints
            port  = 9000
          }
          
          timescaledb = {
            host     = module.databases.timescaledb_endpoint
            port     = module.databases.timescaledb_port
            database = "supersmartmatch_temporal"
            username = "timescale_admin"
            password = random_password.database_passwords["timescale"].result
          }
        }
        
        secrets = {
          encryption_key = module.security.encryption_key
          jwt_secret     = var.jwt_secret
          openai_api_key = var.openai_api_key
        }
        
        monitoring = {
          prometheus_enabled = true
          jaeger_enabled     = true
          grafana_enabled    = true
        }
      }
      
      services = {
        api_gateway = {
          replicas = var.environment == "prod" ? 3 : 1
          resources = {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
          
          ingress = {
            enabled = true
            host    = "api.${var.domain_name}"
            tls     = true
          }
        }
        
        scoring_engine = {
          replicas = var.environment == "prod" ? 5 : 2
          resources = {
            requests = {
              cpu    = "200m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "1000m"
              memory = "2Gi"
            }
          }
          
          nodeSelector = {
            role = "compute"
          }
          
          tolerations = [{
            key      = "compute-intensive"
            operator = "Equal"
            value    = "true"
            effect   = "NoSchedule"
          }]
          
          hpa = {
            enabled = true
            minReplicas = var.environment == "prod" ? 3 : 1
            maxReplicas = var.environment == "prod" ? 20 : 5
            
            metrics = [
              {
                type = "Resource"
                resource = {
                  name = "cpu"
                  target = {
                    type = "Utilization"
                    averageUtilization = 70
                  }
                }
              },
              {
                type = "Resource"
                resource = {
                  name = "memory"
                  target = {
                    type = "Utilization"
                    averageUtilization = 80
                  }
                }
              }
            ]
          }
        }
        
        geolocation_service = {
          replicas = var.environment == "prod" ? 3 : 1
          resources = {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }
        }
        
        temporal_service = {
          replicas = var.environment == "prod" ? 2 : 1
          resources = {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }
        }
        
        behavior_service = {
          replicas = var.environment == "prod" ? 2 : 1
          resources = {
            requests = {
              cpu    = "200m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "1000m"
              memory = "2Gi"
            }
          }
          
          nodeSelector = {
            role = "ml"
          }
          
          tolerations = [{
            key      = "ml-workloads"
            operator = "Equal"
            value    = "true"
            effect   = "NoSchedule"
          }]
        }
        
        explainer_service = {
          replicas = var.environment == "prod" ? 3 : 1
          resources = {
            requests = {
              cpu    = "150m"
              memory = "512Mi"
            }
            limits = {
              cpu    = "750m"
              memory = "1Gi"
            }
          }
        }
        
        analytics_service = {
          replicas = var.environment == "prod" ? 4 : 1
          resources = {
            requests = {
              cpu    = "300m"
              memory = "1Gi"
            }
            limits = {
              cpu    = "2000m"
              memory = "4Gi"
            }
          }
          
          nodeSelector = {
            role = "compute"
          }
          
          tolerations = [{
            key      = "compute-intensive"
            operator = "Equal"
            value    = "true"
            effect   = "NoSchedule"
          }]
        }
      }
    })
  ]
  
  timeout = 600
  
  set_sensitive {
    name  = "global.secrets.jwt_secret"
    value = var.jwt_secret
  }
  
  set_sensitive {
    name  = "global.secrets.openai_api_key"
    value = var.openai_api_key
  }
}
```

### Variables Configuration (variables.tf)

```hcl
# ================================
# CORE VARIABLES
# ================================

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "supersmartmatch-v2"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "owner_team" {
  description = "Team owning this infrastructure"
  type        = string
  default     = "platform-team"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "engineering"
}

# ================================
# NETWORKING VARIABLES
# ================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

variable "enable_vpn_gateway" {
  description = "Enable VPN gateway"
  type        = bool
  default     = false
}

# ================================
# SECURITY VARIABLES
# ================================

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate"
  type        = string
}

variable "waf_rate_limit" {
  description = "WAF rate limit per 5 minutes"
  type        = number
  default     = 2000
}

variable "allowed_countries" {
  description = "List of allowed country codes"
  type        = list(string)
  default     = ["US", "CA", "GB", "FR", "DE", "IT", "ES", "NL", "BE", "CH"]
}

variable "blocked_ips" {
  description = "List of blocked IP addresses"
  type        = list(string)
  default     = []
}

variable "kms_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 30
}

# ================================
# EKS VARIABLES
# ================================

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "cluster_endpoint_public_access" {
  description = "Enable public access to cluster endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDR blocks for public access to cluster endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "eks_node_groups" {
  description = "EKS node groups configuration"
  type = object({
    general = object({
      desired_capacity = number
      max_capacity     = number
      min_capacity     = number
      instance_types   = list(string)
    })
    compute_intensive = object({
      desired_capacity = number
      max_capacity     = number
      min_capacity     = number
      instance_types   = list(string)
    })
    ml_workloads = object({
      desired_capacity = number
      max_capacity     = number
      min_capacity     = number
      instance_types   = list(string)
    })
  })
  
  default = {
    general = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 1
      instance_types   = ["t3.medium", "t3.large"]
    }
    compute_intensive = {
      desired_capacity = 2
      max_capacity     = 20
      min_capacity     = 0
      instance_types   = ["c5.large", "c5.xlarge", "c5.2xlarge"]
    }
    ml_workloads = {
      desired_capacity = 1
      max_capacity     = 5
      min_capacity     = 0
      instance_types   = ["m5.large", "m5.xlarge", "p3.2xlarge"]
    }
  }
}

# ================================
# DATABASE VARIABLES
# ================================

variable "postgres_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "postgres_instance_class" {
  description = "PostgreSQL instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "postgres_allocated_storage" {
  description = "PostgreSQL allocated storage in GB"
  type        = number
  default     = 100
}

variable "postgres_max_allocated_storage" {
  description = "PostgreSQL max allocated storage in GB"
  type        = number
  default     = 1000
}

variable "postgres_backup_retention" {
  description = "PostgreSQL backup retention period in days"
  type        = number
  default     = 7
}

variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_nodes" {
  description = "Number of Redis nodes"
  type        = number
  default     = 1
}

variable "redis_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "redis_parameter_group" {
  description = "Redis parameter group"
  type        = string
  default     = "default.redis7"
}

variable "redis_backup_retention" {
  description = "Redis backup retention period in days"
  type        = number
  default     = 5
}

# ================================
# MONITORING VARIABLES
# ================================

variable "prometheus_storage_size" {
  description = "Prometheus storage size"
  type        = string
  default     = "50Gi"
}

variable "prometheus_retention_period" {
  description = "Prometheus retention period"
  type        = string
  default     = "30d"
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
}

variable "grafana_storage_size" {
  description = "Grafana storage size"
  type        = string
  default     = "10Gi"
}

# ================================
# APPLICATION SECRETS
# ================================

variable "jwt_secret" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

# ================================
# NOTIFICATION VARIABLES
# ================================

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  default     = ""
}

variable "pagerduty_service_key" {
  description = "PagerDuty service key"
  type        = string
  default     = ""
}

variable "email_smtp_host" {
  description = "SMTP host for email alerts"
  type        = string
  default     = ""
}

variable "email_from" {
  description = "From email address for alerts"
  type        = string
  default     = ""
}
```

### Outputs Configuration (outputs.tf)

```hcl
# ================================
# CORE OUTPUTS
# ================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.networking.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.networking.vpc_cidr_block
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.networking.private_subnet_ids
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.networking.public_subnet_ids
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = module.networking.database_subnet_ids
}

# ================================
# EKS OUTPUTS
# ================================

output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster for the OpenID Connect identity provider"
  value       = module.eks.cluster_oidc_issuer_url
}

# ================================
# DATABASE OUTPUTS
# ================================

output "postgres_endpoint" {
  description = "RDS instance endpoint"
  value       = module.databases.postgres_endpoint
  sensitive   = true
}

output "postgres_port" {
  description = "RDS instance port"
  value       = module.databases.postgres_port
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.databases.redis_endpoint
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = 6379
}

output "clickhouse_endpoints" {
  description = "ClickHouse cluster endpoints"
  value       = module.databases.clickhouse_endpoints
  sensitive   = true
}

output "timescaledb_endpoint" {
  description = "TimeScaleDB endpoint"
  value       = module.databases.timescaledb_endpoint
  sensitive   = true
}

# ================================
# SECURITY OUTPUTS
# ================================

output "kms_key_arn" {
  description = "ARN of the KMS key"
  value       = module.security.kms_key_arn
}

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = module.security.waf_web_acl_arn
}

# ================================
# CDN OUTPUTS
# ================================

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = module.cdn.cloudfront_distribution_id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = module.cdn.cloudfront_distribution_arn
}

output "cloudfront_distribution_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = module.cdn.cloudfront_distribution_domain_name
}

# ================================
# APPLICATION OUTPUTS
# ================================

output "application_url" {
  description = "URL of the SuperSmartMatch V2 application"
  value       = "https://${var.domain_name}"
}

output "api_url" {
  description = "URL of the SuperSmartMatch V2 API"
  value       = "https://api.${var.domain_name}/v2"
}

output "grafana_url" {
  description = "URL of the Grafana dashboard"
  value       = "https://grafana.${var.domain_name}"
}

# ================================
# KUBERNETES CONFIG
# ================================

output "kubectl_config" {
  description = "kubectl config command"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

# ================================
# DATABASE CONNECTION STRINGS
# ================================

output "database_connection_info" {
  description = "Database connection information"
  value = {
    postgres = {
      host     = module.databases.postgres_endpoint
      port     = module.databases.postgres_port
      database = "supersmartmatch_core"
      username = "supersmartmatch_admin"
    }
    redis = {
      host = module.databases.redis_endpoint
      port = 6379
    }
    timescaledb = {
      host     = module.databases.timescaledb_endpoint
      port     = module.databases.timescaledb_port
      database = "supersmartmatch_temporal"
      username = "timescale_admin"
    }
  }
  sensitive = true
}
```

Cette configuration Terraform principale déploie :

✅ **Infrastructure complète** : VPC, subnets, security groups  
✅ **Cluster EKS** : Multi-node groups avec auto-scaling  
✅ **Bases de données** : PostgreSQL, Redis, ClickHouse, TimeScaleDB  
✅ **Sécurité** : WAF, KMS, encryption, network isolation  
✅ **Monitoring** : Prometheus, Grafana, Jaeger, ELK  
✅ **CDN** : CloudFront avec optimisations globales  
✅ **Applications** : Deployment automatique des microservices  

La suite : modules détaillés pour chaque composant !
