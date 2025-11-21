import argparse
import json
import os
from agents.analyzer import AnalyzerAgent
from agents.rewriter import RewriterAgent
from agents.validator import ValidatorAgent
from agents.explainer import ExplainerAgent
from openai import OpenAI

PIPELINE_OUTPUT = "agentic-iac/pipeline-result.json"
CHECKOV_FILE = "./checkov-results.json"

# Initialize LLM client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Orchestrator:
    """
    Full Agentic IaC Pipeline:
      1. Analyzer → detect violations from Checkov + TF
      2. Rewriter → auto fix Terraform
      3. Validator → rerun Checkov
      4. Explainer → summary for cloud engineers
    """

    def __init__(self, tf_directory):
        self.tf_directory = tf_directory
        self.analyzer = AnalyzerAgent()
        self.rewriter = RewriterAgent()
        self.validator = ValidatorAgent()
        self.explainer = ExplainerAgent()

    # ---------------------------------------------------------
    # MAIN PIPELINE ENTRY
    # ---------------------------------------------------------
    def run(self):
        print("\n🚀 Starting Agentic IaC Autofix Pipeline")
        print(f"📁 Terraform directory: {self.tf_directory}")

        # =====================================================
        # STEP 0 — Load Checkov scan results
        # =====================================================
        print("\n=== STEP 0: Checking Checkov Results ===")

        if not os.path.exists(CHECKOV_FILE):
            print(f"❌ ERROR: Required file '{CHECKOV_FILE}' not found.")
            print("Make sure GitHub Action step 'Run Checkov' executed.")
            exit(1)

        with open(CHECKOV_FILE, "r") as f:
            checkov_json = json.load(f)

        failed = checkov_json[0]["results"]["failed_checks"]

        # If no violations → skip the entire AI pipeline
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

        # =====================================================
        # STEP 1 — Analyzer Agent
        # =====================================================
        print("\n=== STEP 1: Analyzer Agent ===")
        analysis = self.analyzer.run(self.tf_directory, failed)

        # =====================================================
        # STEP 2 — Rewriter Agent
        # =====================================================
        print("\n=== STEP 2: Rewriter Agent ===")
        rewrite = self.rewriter.run(self.tf_directory, analysis)

        # =====================================================
        # STEP 3 — Validator Agent
        # =====================================================
        print("\n=== STEP 3: Validator Agent ===")
        validation = self.validator.run(self.tf_directory)

        # =====================================================
        # STEP 4 — Explainer Agent
        # =====================================================
        print("\n=== STEP 4: Explainer Agent ===")
        explanation = self.explainer.build_explanation(
            analysis=analysis,
            rewrite=rewrite,
            validation=validation
        )

        # Save pipeline result
        self._save_output(
            status="completed",
            analysis=analysis,
            rewrite=rewrite,
            validation=validation,
            explanation=explanation
        )

        print("\n🎯 Agentic IaC pipeline completed successfully.")
        print(f"📄 Final output saved to: {PIPELINE_OUTPUT}")

    # ---------------------------------------------------------
    # UTILITY — Save complete pipeline output
    # ---------------------------------------------------------
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


# ------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Agentic IaC Autofix Pipeline")
    parser.add_argument("--tf_dir", required=True, help="Path to Terraform modules")

    args = parser.parse_args()
    orch = Orchestrator(tf_directory=args.tf_dir)
    orch.run()
