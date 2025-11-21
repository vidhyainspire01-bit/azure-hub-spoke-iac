import os
import json
from openai import OpenAI

SYSTEM_PROMPT = """
You are an IaC Security Analyzer.
Input: Terraform (.tf) file content.
Output: Structured JSON describing misconfigurations.

Rules:
- Do NOT rewrite code.
- Only detect issues.
- Return array of objects in this format:

[
  {
    "file": "path/to/file.tf",
    "line": 22,
    "issue": "Missing NSG association",
    "severity": "high",
    "fix_hint": "Attach azurerm_network_security_group to this subnet",
    "resource_type": "azurerm_subnet"
  }
]

IMPORTANT:
- Output MUST be valid JSON only.
- Do NOT include explanations or extra text.
"""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AnalyzerAgent:

    def run(self, tf_dir, failed_checks):
        """
        Called by Orchestrator.

        Parameters:
            tf_dir (str): Path to Terraform directory.
            failed_checks (list): Checkov failed checks passed from Orchestrator.

        Returns:
            dict:
            {
                "findings": [...],
                "failed_checks": [...]
            }
        """

        print(f"🔎 AnalyzerAgent scanning Terraform folder: {tf_dir}")

        tf_files = self._collect_tf_files(tf_dir)
        findings = []

        for tf_file in tf_files:
            with open(tf_file, "r") as f:
                content = f.read()

            print(f"📄 Analyzing: {tf_file}")

            # ----------------------------
            # LLM Request
            # ----------------------------
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ]
            )

            raw_output = response.choices[0].message["content"]

            # ----------------------------
            # JSON Parse Safe Block
            # ----------------------------
            try:
                parsed = json.loads(raw_output)

                # Ensure each item includes file reference
                for item in parsed:
                    item["file"] = tf_file
                    findings.append(item)

            except Exception:
                print(f"⚠ LLM returned non-JSON for: {tf_file}")
                print(raw_output)
                continue

        return {
            "findings": findings,
            "failed_checks": failed_checks
        }

    # --------------------------------------------------------
    # Helper: Collect all .tf files
    # --------------------------------------------------------
    def _collect_tf_files(self, tf_dir):
        tf_files = []
        for root, dirs, files in os.walk(tf_dir):
            for f in files:
                if f.endswith(".tf"):
                    tf_files.append(os.path.join(root, f))
        return tf_files
