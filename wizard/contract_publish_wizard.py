from odoo import models, fields, api


class ContractPublishWizard(models.TransientModel):
    _name = "contract.publish_wizard"
    _description = "Contract Publish Wizard"

    contract_id = fields.Many2one("contract.contract", string="Contract", required=True)
    version_id = fields.Many2one(
        "contract.version",
        string="Version to Publish",
        required=True,
        domain="[('contract_id', '=', contract_id)]",
    )

    def action_publish_version(self):
        self.ensure_one()
        contract = self.contract_id
        version = self.version_id

        if version and version.contract_id == contract:
            contract.published_version_id = version
            version.is_published = True
