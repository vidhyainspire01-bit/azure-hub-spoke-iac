from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class AzureTagPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all Azure resources include required tags"
        id = "CKV_CUSTOM_001"
        supported_resources = ["*"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "tags" not in conf:
            return CheckResult.FAILED
        tags = conf.get("tags")[0]
        required = ["environment", "owner"]
        for tag in required:
            if tag not in tags:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AzureTagPolicy()
