from odoo import models, fields, api


class ContractVersionPublishWizard(models.TransientModel):
    _name = "contract.version.publish.wizard"
    _description = "Wizard for Publishing Contract Versions"

    contract_id = fields.Many2one("contract.contract", string="Contract")
    published_version_ids = fields.Many2many(
        "contract.version",
        relation="published_version_ids_rel",
        string="Published Versions",
        readonly=True,
    )
    draft_version_ids = fields.Many2many(
        "contract.version",
        relation="draft_version_ids_rel",
        string="Draft Versions",
        readonly=True,
    )
    version_to_publish_id = fields.Many2one(
        "contract.version", string="Select Version to Publish"
    )

    version_selection = fields.Selection(
        [("draft", "Draft Versions"), ("published", "Published Versions")],
        string="Version Selection",
        default="draft",
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(ContractVersionPublishWizard, self).default_get(fields)
        context = self.env.context
        contract_id = context.get("default_contract_id", False)
        if contract_id:
            contract = self.env["contract.contract"].browse(
                context["default_contract_id"]
            )
            published_version_ids = contract.version_ids - contract.draft_version_ids
            res.update(
                {
                    "draft_version_ids": [(6, 0, contract.draft_version_ids.ids)],
                    "published_version_ids": [(6, 0, published_version_ids.ids)],
                }
            )
        return res

    def action_publish(self):#изменить название
        self.ensure_one()

        self.contract_id.published_version_id = self.version_to_publish_id
        self.version_to_publish_id.is_published = True
        self.contract_id.state = "sign"
        self.contract_id.published_version_id = self.version_to_publish_id
        return {"type": "ir.actions.act_window_close"}
