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
        1. What failed (Analyzer findings)
        2. What was rewritten (Rewriter output)
        3. Whether fixes passed validation
        """

        findings = analysis.get("findings", [])
        failed_checks = analysis.get("failed_checks", [])

        summary = {
            "title": "Agentic IaC Auto-Remediation Report",
            "timestamp": str(datetime.datetime.utcnow()),
            "initial_violations": [],
            "rewrite_actions": [],
            "final_validation": validation,
            "human_summary": ""
        }

        # ----------------------------------------------------
        # 1. INITIAL VIOLATIONS (Analyzer + Checkov Findings)
        # ----------------------------------------------------
        for v in findings:
            summary["initial_violations"].append({
                "file": v.get("file"),
                "line": v.get("line"),
                "issue": v.get("issue"),
                "severity": v.get("severity"),
                "fix_hint": v.get("fix_hint"),
                "resource_type": v.get("resource_type")
            })

        for fc in failed_checks:
            summary["initial_violations"].append({
                "file": fc.get("file_path"),
                "resource": fc.get("resource"),
                "check_id": fc.get("check_id"),
                "check_name": fc.get("check_name")
            })

        # ----------------------------------------------------
        # 2. REWRITER ACTIONS
        # ----------------------------------------------------
        if rewrite and "updated_files" in rewrite:
            for item in rewrite["updated_files"]:
                summary["rewrite_actions"].append({
                    "file": item["file"],
                    "change_summary": item["changes"]
                })

        # ----------------------------------------------------
        # 3. HUMAN SUMMARY
        # ----------------------------------------------------
        if validation.get("status") == "pass":
            summary["human_summary"] = (
                "All violations were successfully corrected by the Agentic Terraform Rewriter.\n"
                "Checkov validation PASSED with zero remaining issues.\n"
                "This PR is safe for merge and deployment."
            )
        else:
            summary["human_summary"] = (
                "The rewriter attempted to fix violations, but Checkov still reports remaining issues.\n"
                "Cloud engineering review is required before merge.\n"
                "See pipeline-result.json for full details."
            )

        return summary
