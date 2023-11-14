from odoo import models, fields, api

class ContractVersionPublishWizard(models.TransientModel):
    _name = "contract.version.publish.wizard"
    _description = "Wizard for Publishing Contract Versions"

    contract_id = fields.Many2one('contract.contract', string="Contract")
    draft_version_ids = fields.Many2many('contract.version', string="Draft Versions", readonly=True)
    version_to_publish_id = fields.Many2one('contract.version', string="Select Version to Publish")

    @api.model
    def default_get(self, fields):
        res = super(ContractVersionPublishWizard, self).default_get(fields)
        context = self.env.context
        if 'default_contract_id' in context and 'draft_version_ids' in context:
            contract = self.env['contract.contract'].browse(context['default_contract_id'])
            res['draft_version_ids'] = [(6, 0, contract.draft_version_ids.ids)]
        return res

    def action_publish(self):
        self.ensure_one()
        if self.version_to_publish_id:
            self.contract_id.published_version_id = self.version_to_publish_id
            self.version_to_publish_id.is_published = True
            self.contract_id.state = 'sign'
            return {'type': 'ir.actions.act_window_close'}
        return {'warning': {'title': "No version selected", 'message': "Please select a version to publish."}}