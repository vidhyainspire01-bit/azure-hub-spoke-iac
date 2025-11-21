import re
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RewriterAgent:

    def apply_fixes(self, findings):
        """
        Apply structured LLM findings to Terraform files.
        Returns list of patched files.
        """

        patched_files = {}

        for finding in findings:
            file_path = finding["file"]
            issue = finding["issue"]
            fix_hint = finding["fix_hint"]

            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue

            with open(file_path, "r") as f:
                content = f.read()

            original_content = content

            # -----------------------------------------------------------------
            # 1. Missing NSG association
            # -----------------------------------------------------------------
            if "NSG" in issue or "security group" in issue.lower():
                content = self._patch_missing_nsg(content)

            # -----------------------------------------------------------------
            # 2. Firewall missing threat intel mode
            # -----------------------------------------------------------------
            if "threat intel" in issue.lower():
                content = self._patch_firewall_threat_intel(content)

            # -----------------------------------------------------------------
            # 3. Firewall missing policy reference
            # -----------------------------------------------------------------
            if "firewall policy" in issue.lower():
                content = self._patch_firewall_policy(content)

            # -----------------------------------------------------------------
            # 4. Missing tags
            # -----------------------------------------------------------------
            if "tag" in issue.lower():
                content = self._patch_tags(content)

            # Save if changed
            if content != original_content:
                with open(file_path, "w") as f:
                    f.write(content)
                patched_files[file_path] = "patched"
                print(f"🔧 Patched: {file_path}")
            else:
                print(f"⚠ No change applied for: {file_path}")

        return patched_files

    # =====================================================================
    #  🔧 Patch Functions
    # =====================================================================

    def _patch_missing_nsg(self, content):
        """
        Looks for an azurerm_subnet block and adds network_security_group_id
        """
        pattern = r'resource\s+"azurerm_subnet"\s+"[\w-]+"\s*{[^}]+}'
        blocks = re.findall(pattern, content, re.DOTALL)

        patched = content

        for block in blocks:
            if "network_security_group_id" not in block:
                updated = block.replace(
                    "address_prefixes",
                    "network_security_group_id = azurerm_network_security_group.default.id\n  address_prefixes"
                )
                patched = patched.replace(block, updated)

        return patched

    def _patch_firewall_threat_intel(self, content):
        """
        Adds threat_intel_mode = \"Deny\" inside azurerm_firewall
        """
        if "resource \"azurerm_firewall\"" not in content:
            return content

        if "threat_intel_mode" in content:
            return content  # already present

        return content.replace(
            "sku_name",
            "threat_intel_mode = \"Deny\"\n  sku_name"
        )

    def _patch_firewall_policy(self, content):
        """
        Adds firewall_policy_id = azurerm_firewall_policy.hub_policy.id
        """
        if "resource \"azurerm_firewall\"" not in content:
            return content

        if "firewall_policy_id" in content:
            return content

        return content.replace(
            "sku_name",
            "firewall_policy_id = azurerm_firewall_policy.hub_policy.id\n  sku_name"
        )

    def _patch_tags(self, content):
        """
        Ensures tags block exists with required enterprise tags.
        """

        required_tags = """
  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
"""

        # If tags block missing
        if "tags" not in content:
            return content.replace("}", required_tags + "}")

        return content
