from email.policy import strict
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name_genitive = fields.Char(
        string="Full name in genitive",
    )
    name_initials = fields.Char(
        string="Surname and initials",
    )
    position_genitive = fields.Char(
        string="Position genitive",
    )
    partner_contract_ids = fields.One2many(
        comodel_name="contract.contract",
        inverse_name="partner_id",
        string="Contracts",
    )
    contract_count = fields.Integer(
        compute="_compute_contract_count",
        string="# of contracts",
        search=True,
    )
    representative_id = fields.Many2one(
        "res.partner", string="Representative", help="Person representing company"
    )
    representative_document = fields.Char(
        string="Representative acts on the basis of",
        help="Parent Case",
    )

    @api.depends("self.partner_contract_ids")
    def _compute_contract_count(self):
        self.ensure_one()
        self.contract_count = len(self.partner_contract_ids)
