import argparse
import json
import os
from agents.analyzer import AnalyzerAgent
from agents.rewriter import RewriterAgent
from agents.validator import ValidatorAgent
from agents.explainer import ExplainerAgent
from openai import OpenAI

# Final output
PIPELINE_OUTPUT = "agentic-iac/pipeline-result.json"

# Correct Checkov output path
CHECKOV_FILE = os.path.join(os.getcwd(), "reports", "results_json.json")
print("Looking for Checkov output at:", CHECKOV_FILE)

# LLM client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Orchestrator:
    def __init__(self, tf_directory):
        self.tf_directory = tf_directory
        self.analyzer = AnalyzerAgent()
        self.rewriter = RewriterAgent()
        self.validator = ValidatorAgent()
        self.explainer = ExplainerAgent()

    def run(self):
        print("\n🚀 Starting Agentic IaC Autofix Pipeline")
        print(f"📁 Terraform directory: {self.tf_directory}")

        # STEP 0 — Load Checkov Results
        print("\n=== STEP 0: Checking Checkov Results ===")

        if os.path.isdir(CHECKOV_FILE):
            print(f"⚠️ WARNING: '{CHECKOV_FILE}' is a directory. Removing it...")
            os.system(f"rm -rf '{CHECKOV_FILE}'")

        if not os.path.isfile(CHECKOV_FILE):
            print(f"❌ ERROR: Required file '{CHECKOV_FILE}' not found.")
            exit(1)

        with open(CHECKOV_FILE, "r") as f:
            checkov_json = json.load(f)

        if "results" not in checkov_json:
            print("❌ ERROR: Invalid Checkov JSON format. 'results' key missing.")
            print("File content:", checkov_json)
            exit(1)

        failed = checkov_json["results"].get("failed_checks", [])

        if not isinstance(failed, list):
            print("❌ ERROR: failed_checks is not a list.")
            exit(1)

        print(f"Found {len(failed)} failed checks")


        if len(failed) == 0:
            print("🎉 No violations found. Skipping Analyzer/Rewriter/Validator steps.")
            explanation = self.explainer.build_no_violation_report()

            self._save_output(
                status="no-change",
                analysis={"failed_checks": []},
                rewrite=None,
                validation=None,
                explanation=explanation
            )
            return

        print("\n=== STEP 1: Analyzer Agent ===")
        analysis = self.analyzer.run(self.tf_directory, failed)

        print("\n=== STEP 2: Rewriter Agent ===")
        rewrite = self.rewriter.run(self.tf_directory, analysis)

        print("\n=== STEP 3: Validator Agent ===")
        validation = self.validator.run(self.tf_directory)

        print("\n=== STEP 4: Explainer Agent ===")
        explanation = self.explainer.build_explanation(
            analysis=analysis,
            rewrite=rewrite,
            validation=validation
        )

        self._save_output(
            status="completed",
            analysis=analysis,
            rewrite=rewrite,
            validation=validation,
            explanation=explanation
        )

        print("\n🎯 Agentic IaC pipeline completed successfully.")
        print(f"📄 Final output saved to: {PIPELINE_OUTPUT}")

    def _save_output(self, status, analysis, rewrite, validation, explanation):
        result = {
            "status": status,
            "analysis": analysis,
            "rewrite": rewrite,
            "validation": validation,
            "explanation": explanation
        }

        os.makedirs(os.path.dirname(PIPELINE_OUTPUT), exist_ok=True)

        with open(PIPELINE_OUTPUT, "w") as f:
            json.dump(result, f, indent=4)

        print(f"📝 Output saved → {PIPELINE_OUTPUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Agentic IaC Autofix Pipeline")
    parser.add_argument("--tf_dir", required=True, help="Path to Terraform modules")

    args = parser.parse_args()
    orch = Orchestrator(tf_directory=args.tf_dir)
    orch.run()
