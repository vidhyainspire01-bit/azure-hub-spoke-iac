import subprocess
import json
import os
import tempfile


class ValidatorAgent:
    """
    Runs Checkov on rewritten Terraform files and reports
    remaining violations after autofix is applied.
    """

    def run(self, tf_directory):
        print(f"🔍 Running validation scan on: {tf_directory}")

        # Checkov v3 writes files inside a directory
        output_dir = tempfile.mkdtemp(prefix="agentic_checkov_")
        results_file = os.path.join(output_dir, "results_json.json")

        cmd = [
            "checkov",
            "-d", tf_directory,
            "--output", "json",
            "--output-file-path", output_dir,
            "--quiet"
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("❌ Checkov failed:", e.stderr.decode())
            return {
                "status": "error",
                "message": "Checkov execution failed",
                "raw_error": e.stderr.decode()
            }

        # -----------------------------------------------------------------
        # Check if Checkov produced the file
        # -----------------------------------------------------------------
        if not os.path.exists(results_file):
            return {
                "status": "error",
                "message": f"Checkov did not create results_json.json in {output_dir}"
            }

        # Load JSON results
        with open(results_file, "r") as f:
            data = json.load(f)

        failed = []
        passed = []

        for block in data:
            results = block.get("results", {})
            failed_checks = results.get("failed_checks", [])
            passed_checks = results.get("passed_checks", [])

            for fc in failed_checks:
                failed.append({
                    "file": fc.get("file_path"),
                    "resource": fc.get("resource"),
                    "check_id": fc.get("check_id"),
                    "check_name": fc.get("check_name")
                })

            for pc in passed_checks:
                passed.append({
                    "file": pc.get("file_path"),
                    "resource": pc.get("resource"),
                    "check_id": pc.get("check_id")
                })

        summary = {
            "total_passed": len(passed),
            "total_failed": len(failed),
            "failed_checks": failed,
            "passed_checks": passed,
        }

        # -----------------------------------------------------------------
        # Final Evaluation
        # -----------------------------------------------------------------
        if len(failed) == 0:
            print("✅ Validation SUCCESS — all issues resolved.")
            return {
                "status": "pass",
                "summary": summary,
                "details": data
            }

        print("⚠ Validation FAILED — some violations remain.")
        return {
            "status": "fail",
            "summary": summary,
            "details": data
        }
