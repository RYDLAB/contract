from odoo import fields, models, api
from odoo.exceptions import UserError


class ContractSection(models.Model):
    _name = "contract.section"
    _description = "Contract Section"
    _order = "sequence"

    name = fields.Char(string="Name")
    sequence = fields.Integer()
    contract_id = fields.Many2one("contract.contract", string="Contract")
    line_ids = fields.One2many("contract.line", "section_id", string="Section text")
    version_id = fields.Many2one("contract.version", string="Contract Version")

    @api.constrains("name", "version_id", "line_ids", "contract_id")
    def _check_published_version(self):
        for record in self:
            if record.version_id.is_published:
                raise UserError(
                    "Cannot modify a section of a published contract version."
                )

    def button_create_clause(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Create Line",
            "view_mode": "form",
            "res_model": "contract.line",
            "context": {
                "default_section_id": self.id,
                "default_contract_id": self.contract_id.id,
                "default_version_id": self.version_id.id,
            },
            "target": "new",
        }
