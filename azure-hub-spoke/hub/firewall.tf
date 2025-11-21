resource "azurerm_firewall" "hub_fw" {
  name                = "hub-firewall"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  sku_name            = "AZFW_VNet"
  sku_tier            = "Standard" 

  threat_intel_mode   = "Deny"
  firewall_policy_id  = azurerm_firewall_policy.hub_policy.id

  ip_configuration {
    name                 = "fw-config"
    subnet_id            = azurerm_subnet.AzureFirewallSubnet.id
    public_ip_address_id = azurerm_public_ip.fw_pip.id
  }
}

resource "azurerm_network_security_group" "bad_nsg" {
  name                = "bad-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_network_security_rule" "bad_rule" {
  name                       = "open-to-world"
  priority                   = 100
  direction                  = "Inbound"
  access                     = "Allow"
  protocol                   = "*"
  source_port_range          = "*"
  destination_port_range     = "22"
  source_address_prefix      = "*"
  destination_address_prefix = "*"

  # associate this rule with the NSG created above
  network_security_group_name = azurerm_network_security_group.bad_nsg.name
  resource_group_name         = azurerm_network_security_group.bad_nsg.resource_group_name
}



resource "azurerm_public_ip" "fw_pip" {
  name                = "fw-public-ip"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  allocation_method   = "Static"
  sku_tier            = "Standard" 

  tags = {
    environment = "prod"
    owner       = "vidhya"
  }
}
