import os
import re
import json


class RewriterAgent:

    # ==========================================================
    # MAIN ENTRYPOINT (orchestrator calls this)
    # ==========================================================
    def run(self, tf_dir, analysis):
        """
        tf_dir: terraform directory
        analysis: dict returned from AnalyzerAgent.run()
        {
            "findings": [...],
            "failed_checks": [...]
        }
        """

        findings = analysis.get("findings", [])

        print(f"🛠 RewriterAgent: {len(findings)} findings received")

        patched_files = self.apply_fixes(findings)

        return {
            "updated_files": [
                {"file": f, "changes": "autofixed"}
                for f in patched_files.keys()
            ],
            "count": len(patched_files)
        }

    # ==========================================================
    # APPLY FIXES
    # ==========================================================
    def apply_fixes(self, findings):
        patched_files = {}

        for finding in findings:
            file_path = finding.get("file")
            issue = finding.get("issue", "")
            fix_hint = finding.get("fix_hint", "")

            if not file_path or not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue

            print(f"\n➡ Applying fix for issue: {issue}")
            print(f"📄 File: {file_path}")
            print(f"💡 Hint: {fix_hint}")

            with open(file_path, "r") as f:
                content = f.read()

            original_content = content

            # ----------------------------
            # 🔹 RULE-BASED PATCHES
            # ----------------------------
            lowered = issue.lower()

            if "nsg" in lowered or "security" in lowered:
                content = self._patch_missing_nsg(content)

            if "threat intel" in lowered:
                content = self._patch_firewall_threat_intel(content)

            if "firewall policy" in lowered:
                content = self._patch_firewall_policy(content)

            if "tag" in lowered:
                content = self._patch_tags(content)

            # ----------------------------
            # SAVE IF CHANGED
            # ----------------------------
            if content != original_content:
                with open(file_path, "w") as f:
                    f.write(content)

                patched_files[file_path] = "patched"
                print(f"✅ FIXED: {file_path}")

            else:
                print(f"⚠ No changes required for: {file_path}")

        return patched_files

    # ==========================================================
    # PATCH FUNCTIONS
    # ==========================================================

    def _patch_missing_nsg(self, content):
        """
        Add missing network_security_group_id to azurerm_subnet
        """
        pattern = r'(resource\s+"azurerm_subnet"\s+"[\w-]+"\s*{[^}]*?)address_prefixes'
        replacement = (
            r'\1network_security_group_id = azurerm_network_security_group.default.id\n  address_prefixes'
        )

        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return new_content

    def _patch_firewall_threat_intel(self, content):
        """
        Adds threat_intel_mode = "Deny"
        inside azurerm_firewall resources.
        """

        if "resource \"azurerm_firewall\"" not in content:
            return content

        if "threat_intel_mode" in content:
            return content

        return content.replace(
            "sku_name",
            "threat_intel_mode = \"Deny\"\n  sku_name"
        )

    def _patch_firewall_policy(self, content):
        """
        Adds firewall_policy_id for azure firewall.
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
        Ensures that a tags block exists.
        """

        required_tags = """
  tags = {
    environment = "dev"
    owner       = "vidhya"
  }
"""

        if "tags" in content:
            return content

        # insert tags before the last '}'
        return content.rstrip("}") + required_tags + "}"
