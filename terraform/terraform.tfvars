location            = "Australia East"
resource_group_name = "week09-rg"

# Replace with a unique name for your Azure Container Registry 
acr_name             = "benbaijuweek09acr"

# Replace with a unique name for your Azure Storage Account
storage_account_name = "benbaijuweek09storage"

# Replace with a unique name for your Azure Kubernetes Service cluster
aks_cluster_name = "week09-aks"
aks_dns_prefix   = "koalatech"

aks_node_count   = 3
aks_node_vm_size = "Standard_D2s_v3"

environment = "development"

tags = {
    Project    = "KoalaTech Course Platform"
    ManagedBy  = "Terraform"
    Practical  = "week09"
    Environment = "Development"
}