import datetime


class ExplainerAgent:
    """
    Builds a human-readable explanation for engineers and reviewers.
    """

    def build_no_violation_report(self):
        return {
            "title": "Terraform Clean — No Violations Found",
            "timestamp": str(datetime.datetime.utcnow()),
            "message": (
                "Checkov found no policy violations in the submitted Terraform module.\n"
                "No rewriting or corrections were required.\n"
                "Pipeline completed successfully."
            )
        }

    def build_explanation(self, analysis, rewrite, validation):
        """
        Build a detailed explanation covering:
        1. What failed
        2. What was rewritten
        3. Whether fixes passed validation
        """

        summary = {
            "title": "Agentic IaC Auto-Remediation Report",
            "timestamp": str(datetime.datetime.utcnow()),
            "initial_violations": [],
            "rewrite_actions": [],
            "final_validation": {},
            "human_summary": ""
        }

        # ---------------------------
        # 1. INITIAL VIOLATIONS
        # ---------------------------
        for v in analysis.get("failed_checks", []):
            summary["initial_violations"].append({
                "resource": v.get("resource"),
                "file": v.get("file"),
                "check_id": v.get("check_id"),
                "check_name": v.get("check_name"),
            })

        # ---------------------------
        # 2. REWRITER ACTIONS
        # ---------------------------
        if rewrite and rewrite.get("updated_files"):
            for item in rewrite["updated_files"]:
                summary["rewrite_actions"].append({
                    "file": item["file"],
                    "change_summary": item["changes"]
                })

        # ---------------------------
        # 3. FINAL VALIDATION
        # ---------------------------
        summary["final_validation"] = validation

        # ---------------------------
        # 4. HUMAN SUMMARY
        # ---------------------------
        if validation["status"] == "pass":
            summary["human_summary"] = (
                "All violations were successfully corrected by the Agentic Terraform Rewriter.\n"
                "Checkov validation PASSED with zero remaining issues.\n"
                "This PR is safe for merge and deployment."
            )
        else:
            summary["human_summary"] = (
                "The rewriter attempted to fix the issues, but Checkov still reports violations.\n"
                "Cloud engineering review is required.\n"
                "Please check the full details in pipeline-result.json."
            )

        return summary
