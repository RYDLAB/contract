from odoo import models, fields, api


class ContractContentWizard(models.TransientModel):
    _name = "contract.content.wizard"
    _description = "Wizard to edit contract content"

    content = fields.Text("Content", required=True)

    def button_save(self):
        line_id = self.env.context.get("active_id", False)

        if line_id:
            line = self.env["contract.line"].browse(line_id)

            existing_content = self.find_existing_content(line)

            if not existing_content:
                self.save_new_content(line)

    def find_existing_content(self, line):
        return self.env["contract.content"].search(
            [("content", "=", self.content), ("line_ids", "in", [line.id])], limit=1
        )

    def save_new_content(self, line):
        new_content = self.env["contract.content"].create({"content": self.content})
        line.write(
            {
                "content_ids": [(4, new_content.id)],
                "current_content_id": new_content.id,
            }
        )
