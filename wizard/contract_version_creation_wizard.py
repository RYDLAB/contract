from odoo import models, fields, api
from odoo.exceptions import UserError


class ContractVersionCreationWizard(models.TransientModel):
    _name = "contract.version.creation.wizard"
    _description = "Wizard for Creating New Contract Version"

    contract_id = fields.Many2one("contract.contract", string="Contract", required=True)
    base_version_id = fields.Many2one(
        "contract.version",
        string="Base Version",
        required=True,
        domain="[('contract_id', '=', contract_id)]",
    )

    def button_create_new_version(self):
        self.ensure_one()
        contract = self.contract_id
        base_version = self.base_version_id

        last_version = self.env["contract.version"].search(
            [("contract_id", "=", self.base_version_id.contract_id.id)],
            order="version_number desc",
            limit=1,
        )
        new_version_number = int(last_version) + 1
        new_version = self.env["contract.version"].create(
            {
                "contract_id": contract.id,
                "version_number": str(new_version_number),
            }
        )

        for section in base_version.section_ids:
            new_section = section.copy({"version_id": new_version.id})
            for line in section.line_ids:
                line.copy({"section_id": new_section.id, "contract_id": contract.id})

        return {"type": "ir.actions.act_window_close"}
