from odoo import models, fields, api


class ContractLine(models.Model):
    """Хранит информацию о пунктах(абзацах) договора."""

    _name = "contract.line"
    _description = "Contract Line"
    _order = "create_date desc"

    section_id = fields.Many2one("contract.section", string="Раздел")
    contract_id = fields.Many2one("contract.contract", string="Договор")
    number = fields.Char(string="Номер")
    sequence = fields.Integer(string="Sequence")
    create_date = fields.Datetime(string="Дата создания")
    content_ids = fields.Many2many(
        "contract.content",
        "contract_line_content_rel",
        "line_id",
        "content_id",
        string="Содержимое",
    )
    current_content_id = fields.Many2one(
        "contract.content", string="Актуальное содержимое"
    )
    current_content_text = fields.Text(
        string="Текст актуального содержимого",
        related="current_content_id.content",
        readonly=True,
    )

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        """Создает копию текущего пункта договора."""
        default = dict(default or {})

        default["current_content_id"] = self.current_content_id.id
        new_line = super(ContractLine, self).copy(default)

        new_line.write({"content_ids": [(6, 0, self.current_content_id.ids)]})

        return new_line

    def button_show_history(self):
        """Отображает историю изменений содержимого пункта договора."""

        return {
            "name": "История Содержимого",
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
            "name": "Редактировать пункт",
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
