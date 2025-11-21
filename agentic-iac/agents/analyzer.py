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
- Return array of objects:
  [{
     "file": "...",
     "line": 22,
     "issue": "Missing NSG association",
     "severity": "high",
     "fix_hint": "Attach azurerm_network_security_group to this subnet",
     "resource_type": "azurerm_subnet"
   }]
"""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AnalyzerAgent:

    def analyze(self, tf_files):
        findings = []

        for tf_file in tf_files:
            with open(tf_file, "r") as f:
                content = f.read()

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ]
            )

            try:
                result = json.loads(response.choices[0].message["content"])
                for item in result:
                    item["file"] = tf_file
                    findings.append(item)
            except Exception:
                print(f"⚠ LLM returned non-JSON for {tf_file}")

        return findings
