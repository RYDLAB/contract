from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fullname = fields.Char(
        string="Full name",
        help="Full name eg. Ivanov Ivan Ivanovich"
    )

    fullname_genitive = fields.Char(
        string="Full name in genitive",
        help="Full name in the genitive eg. Ivanova Ivana Ivanovicha"
    )

    surname_initials = fields.Char(
        string="Surname and initials",
        help="Surname and initials eg. Ivanov I. I."
    )

    position = fields.Char(
        string="Position",
        help="Position: eg. director"
    )

    position_genitive = fields.Char(
        string="Position in genitive",
        help="Position in genitive: eg. directora"
    )

    partner_contract_ids = fields.One2many(
        comodel_name="contract.contract",
        inverse_name="partner_id",
        string="Contracts",
    )
    contract_count = fields.Integer(
        compute="_compute_contract_count", string="# of contracts"
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
