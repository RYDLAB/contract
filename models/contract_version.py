from odoo import fields, models, api
from odoo.exceptions import UserError
class ContractVersion(models.Model):
    _name="contract.version"
    _description="Contract Version"

    name = fields.Char(string="Name", compute='_compute_name', store=True)
    version_number = fields.Integer(string="Version Number", required=True)

    contract_id = fields.Many2one('contract.contract', string="Contract", required=True)
    section_ids = fields.One2many('contract.section', 'version_id', string="Sections")

    is_published = fields.Boolean(string="Published")

    @api.depends('contract_id.name', 'version_number')
    def _compute_name(self):
        for record in self:
            record.name = '{} - {}'.format(record.contract_id.name, record.version_number)

    def publish_version(self):
        """ Метод для публикации версии. """
        self.ensure_one()
        if self.contract_id.state == 'sign':
            raise UserError("Cannot publish a new version of a signed contract.")

        if not self.is_published:
            self.write({'is_published': True})
            self.contract_id.write({'published_version_id': self.id})

