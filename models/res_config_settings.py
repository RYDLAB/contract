# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_not_signed_contract = fields.Boolean(
        string="Allow binding annexes to unsigned contracts",
        help="If switched off, binding annexes is possible for signed contracts only",
    )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"]
        ir_config.set_param(
            "contract.allow_not_signed_contract", self.allow_not_signed_contract
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        allow_not_signed_contract = ir_config.get_param(
            "contract.allow_not_signed_contract"
        )
        res.update({"allow_not_signed_contract": allow_not_signed_contract})
        return res
