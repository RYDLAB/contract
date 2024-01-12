from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractLine(models.Model):
    """Хранит информацию о пунктах(абзацах) договора."""

    _name = "contract.line"
    _description = "Contract Line"
    _order = "sequence"

    section_id = fields.Many2one("contract.section", string="Section")
    contract_id = fields.Many2one("contract.contract", string="Contract")
    number = fields.Char(string="Number")
    sequence = fields.Integer()
    create_date = fields.Datetime(string="Creation date")
    content_ids = fields.Many2many(
        "contract.content",
        "contract_line_content_rel",
        "line_id",
        "content_id",
        string="Content",
        copy=False,
    )
    current_content_id = fields.Many2one("contract.content", string="Actual content")
    current_content_text = fields.Text(
        string="Actual content text",
        related="current_content_id.content",
        readonly=True,
    )

    history_count = fields.Integer(
        string="History Count", compute="_compute_history_count", store=False
    )

    @api.depends("content_ids")
    def _compute_history_count(self):
        for record in self:
            record.history_count = len(record.content_ids)

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        """Создает копию текущего пункта договора."""
        default = dict(default or {})
        default.update(
            {
                "current_content_id": self.current_content_id.id,
                "content_ids": ([(6, 0, self.current_content_id.ids)]),
            }
        )
        return super(ContractLine, self).copy(default)

    @api.constrains("section_id", "contract_id", "number", "content_ids")
    def _check_published_version(self):
        for record in self:
            if record.section_id.version_id.is_published:
                raise UserError(
                    _("Cannot modify a line of a published contract version.")
                )

    def button_delete_content(self):
        self.ensure_one()
        return {
            "name": _("Confirm Deletion"),
            "type": "ir.actions.act_window",
            "res_model": "confirm.deletion.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_confirm_message": _(
                    "Are you sure you want to delete: %s", self.number
                ),
                "active_model": self._name,
                "active_id": self.id,
            },
        }

    def button_show_history(self):
        """Отображает историю изменений содержимого пункта договора."""

        return {
            "name": _("Content history"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "contract.content",
            "domain": [("id", "in", self.content_ids.ids)],
            "context": {"active_id": self.id},
        }

    def button_edit_content(self):
        """Открывает визард для редактирования содержимого текущего пункта договора."""

        return {
            "name": _("Edit clause"),
            "type": "ir.actions.act_window",
            "res_model": "contract.content.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("contract.view_contract_content_wizard_form").id,
            "target": "new",
            "context": {
                "default_content": self.current_content_id.content,
                "active_current_id": self.current_content_id.id,
                "active_id": self.id,
            },
        }
