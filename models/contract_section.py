from odoo import fields, models
from odoo.exceptions import UserError


class ContractSection(models.Model):
    _name = "contract.section"
    _description = "Contract Section"
    _order = "sequence"

    name = fields.Char(string="Name")
    sequence = fields.Integer()
    contract_id = fields.Many2one("contract.contract", string="Contract")
    line_ids = fields.One2many("contract.line", "section_id", string="Section text")

    def button_create_clause(self):
        raise UserError("Button 'New clause' works")
