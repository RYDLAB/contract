from odoo import models, fields, api
from odoo.exceptions import UserError


class ContractContent(models.Model):
    _name = "contract.content"
    _description = "Contract Content"

    content = fields.Text(string="Text")
    line_ids = fields.Many2many(
        "contract.line",
        "contract_line_content_rel",
        "content_id",
        "line_id",
        string="Сlauses",
    )

    @api.model_create_multi
    def create(self, vals):
        new_content = super(ContractContent, self).create(vals)
        for line in new_content.line_ids:
            line.current_content_id = new_content.id
        return new_content

    @api.constrains("content", "line_ids")
    def _check_published_version(self):
        for record in self:
            if any(line.section_id.version_id.is_published for line in record.line_ids):
                raise UserError(
                    "Cannot modify the content of a published contract version."
                )

    def write(self, vals):
        if "content" in vals:
            new_content = self._create_new_content(vals)
            for rec in self:
                rec.line_ids.write({"current_content_id": new_content.id})
            return True
        return super(ContractContent, self).write(vals)

    def button_make_current(self):
        self.ensure_one()
        line_id = self.env.context.get("active_id", False)
        self.env["contract.line"].browse(line_id).write({"current_content_id": self.id})

    def _create_new_content(self, vals):
        new_vals = vals.copy()
        new_vals["line_ids"] = [(6, 0, self.line_ids.ids)]
        return self.create(new_vals)
