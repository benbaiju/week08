resource "azurerm_log_analytics_workspace" "aks" {
  name                = "${var.aks_cluster_name}-logs"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

output "log_analytics_workspace_id" {
  description = "Workspace (customer) ID — set GitHub Actions repo variable LOG_ANALYTICS_WORKSPACE_ID to this value"
  value       = azurerm_log_analytics_workspace.aks.workspace_id
}

output "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace used by AKS Azure Monitor"
  value       = azurerm_log_analytics_workspace.aks.name
}

output "log_analytics_workspace_resource_id" {
  description = "ARM resource ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.aks.id
}
