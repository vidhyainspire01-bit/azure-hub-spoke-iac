resource "azurerm_firewall" "hub_fw" {
  name                = "hub-firewall"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  sku_name            = "AZFW_VNet"

  threat_intel_mode   = "Deny"
  firewall_policy_id  = azurerm_firewall_policy.hub_policy.id

  ip_configuration {
    name                 = "fw-config"
    subnet_id            = azurerm_subnet.AzureFirewallSubnet.id
    public_ip_address_id = azurerm_public_ip.fw_pip.id
  }
}


resource "azurerm_public_ip" "fw_pip" {
  name                = "fw-public-ip"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    environment = "prod"
    owner       = "vidhya"
  }
}
