import subprocess
import json
import os
import tempfile


class ValidatorAgent:
    """
    Runs Checkov on patched Terraform and validates fixes.
    """

    def run(self, tf_directory):
        """
        Execute Checkov scan on updated Terraform files.
        """

        print(f"🔍 Running validation on: {tf_directory}")

        results_file = os.path.join(tempfile.gettempdir(), "agentic_checkov_results.json")

        cmd = [
            "checkov",
            "-d", tf_directory,
            "--output", "json",
            "--output-file-path", results_file,
            "--quiet"
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("❌ Checkov failed to run:", e.stderr.decode())
            return {
                "status": "error",
                "message": "Checkov execution failed",
                "raw_error": e.stderr.decode()
            }

        if not os.path.exists(results_file):
            return {
                "status": "error",
                "message": "Checkov did not produce output file"
            }

        with open(results_file, "r") as f:
            data = json.load(f)

        failed = []
        passed = []

        for block in data:
            results = block.get("results", {})
            failed_checks = results.get("failed_checks", [])
            passed_checks = results.get("passed_checks", [])

            for fcheck in failed_checks:
                failed.append({
                    "file": fcheck.get("file_path"),
                    "resource": fcheck.get("resource"),
                    "check_id": fcheck.get("check_id"),
                    "check_name": fcheck.get("check_name")
                })

            for pcheck in passed_checks:
                passed.append({
                    "file": pcheck.get("file_path"),
                    "resource": pcheck.get("resource"),
                    "check_id": pcheck.get("check_id")
                })

        summary = {
            "total_passed": len(passed),
            "total_failed": len(failed),
            "failed_checks": failed,
            "passed_checks": passed,
        }

        if len(failed) == 0:
            print("✅ Validation SUCCESS — no Checkov failures remain.")
            return {
                "status": "pass",
                "summary": summary,
                "details": data
            }

        print("⚠ Validation FAILED — issues remain after rewriting.")
        return {
            "status": "fail",
            "summary": summary,
            "details": data
        }
