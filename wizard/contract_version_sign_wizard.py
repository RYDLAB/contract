from odoo import models, fields, api


class ContractVersionSignWizard(models.TransientModel):
    _name = "contract.version.sign.wizard"
    _description = "Wizard for Signing Contract Versions"

    contract_id = fields.Many2one("contract.contract", string="Contract")
    published_version_id = fields.Many2one(
        "contract.version",
        string="Published Version",
        readonly=True,
    )

    version_selection = fields.Selection(
        [("empty", "Without Versions"), ("published", "Published Version")],
        string="Version Selection",
        default="empty",
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(ContractVersionSignWizard, self).default_get(fields)
        context = self.env.context
        contract_id = context.get("default_contract_id", False)
        if contract_id:
            published_version_id = context.get("published_version_id", False)
            res.update(
                {
                    "published_version_id": published_version_id,
                }
            )
        return res

    def action_sign(self):
        self.ensure_one()
        self.contract_id.state = "sign"
        if self.version_selection == "published":
            self.contract_id.signed_version_id = self.published_version_id
            self.contract_id.signed_version_id.is_signed = True
        else:
            self.contract_id.signed_version_id = False
        return {"type": "ir.actions.act_window_close"}
