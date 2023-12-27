from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ContractVersion(models.Model):
    _name = "contract.version"
    _description = "Contract Version"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    version_number = fields.Integer(string="Version Number", required=True)

    contract_id = fields.Many2one("contract.contract", string="Contract", required=True)
    section_ids = fields.One2many("contract.section", "version_id", string="Sections")

    is_published = fields.Boolean(string="Published")

    @api.depends("contract_id.name", "version_number")
    def _compute_name(self):
        for record in self:
            record.name = "{} - {}".format(
                record.contract_id.name, record.version_number
            )

    def publish_version(self):
        """Метод для публикации версии."""
        self.ensure_one()
        if self.contract_id.state == "sign":
            raise UserError("Cannot publish a new version of a signed contract.")

        if not self.is_published:
            self.write({"is_published": True})
            self.contract_id.write({"published_version_id": self.id})

    def rollback_unpublish_version(self):
        self.ensure_one()
        if self.is_published:
            if self.contract_id.state == "sign":
                raise UserError("Cannot rollback publish version of a signed contract.")
            self.is_published = False
            if self.contract_id.published_version_id.id == self.id:
                published_vers = (
                    self.contract_id.mapped("version_ids")
                    .filtered(lambda rec: rec.is_published)
                    .sorted("create_date", reverse=True)
                )
                self.contract_id.published_version_id = (
                    published_vers[0] if published_vers else False
                )

    def button_create_section(self):
        self.ensure_one()
        return {
            "name": _("Create Contract Section"),
            "type": "ir.actions.act_window",
            "res_model": "contract.section.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("contract.view_contract_section_wizard_form").id,
            "target": "new",
            "context": {
                "default_version_id": self.id,
                "default_contract_id": self.contract_id.id,
            },
        }
