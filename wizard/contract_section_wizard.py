from odoo import models, fields, api
from odoo.exceptions import UserError


class ContractSectionWizard(models.TransientModel):
    _name = "contract.section.wizard"
    _description = "Wizard to Create a Contract Section"

    version_id = fields.Many2one("contract.version", string="Contract Version")
    contract_id = fields.Many2one("contract.contract", string="Contract")
    name = fields.Char(string="Section Name", required=True)

    def button_create(self):
        self.ensure_one()
        if not self.name:
            raise UserError("Section name can't be empty.")

        self.env["contract.section"].create(
            {
                "name": self.name,
                "version_id": self.version_id.id,
                "contract_id": self.contract_id.id,
            }
        )
        return {"type": "ir.actions.act_window_close"}
