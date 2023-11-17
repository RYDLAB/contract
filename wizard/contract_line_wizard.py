from odoo import models, fields, api
from odoo.exceptions import UserError


class ContractLineWizard(models.TransientModel):
    _name = "contract.line.wizard"
    _description = "Wizard to Create a Contract Line"

    section_id = fields.Many2one("contract.section", string="Section")
    contract_id = fields.Many2one("contract.contract", string="Contract")
    content_text = fields.Text(string="Content")
    number = fields.Char(string="Number")

    def button_create(self):
        self.ensure_one()
        if not self.content_text:
            raise UserError("Content can't be empty.")

        content = self.env["contract.content"].create({"content": self.content_text})

        new_line = self.env["contract.line"].create(
            {
                "section_id": self.section_id.id,
                "contract_id": self.contract_id.id,
                "current_content_id": content.id,
                "content_ids": [(6, 0, [content.id])],
                "number": self.number,
            }
        )
        return {"type": "ir.actions.act_window_close"}
