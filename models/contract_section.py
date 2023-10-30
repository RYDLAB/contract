from odoo import models, fields, api


class ContractSection(models.Model):
    _name = "contract.section"
    _description = "Contract Section"
    _order = "sequence"

    name = fields.Char(string="Название")
    sequence = fields.Integer(string="Порядок")
    contract_id = fields.Many2one("contract.contract", string="Договор")
    line_ids = fields.One2many("contract.line", "section_id", string="Пункты")
