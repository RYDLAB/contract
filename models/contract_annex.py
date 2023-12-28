import math

from odoo import _, api, fields, models


class ContractAnnex(models.Model):
    _name = "contract.annex"
    _description = "Contract Annex"

    name = fields.Char(
        string="Name",
    )
    display_name = fields.Char(
        compute="_compute_display_name",
    )
    # specification_name = fields.Char(
    #     compute="_compute_specification_name",
    # )

    contract_id = fields.Many2one(
        "contract.contract",
        string="Contract",
        readonly=True,
    )
    contract_type = fields.Selection(
        related="contract_id.type",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="contract_id.company_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="contract_id.partner_id",
    )
    date_conclusion = fields.Date(
        string="Signing Date",
        default=fields.Date.today(),
    )
    annex_number = fields.Integer(
        string="№",
        help="Number of current annex among other annexes",
    )
    currency_id = fields.Many2one(
        related="contract_id.currency_id",
    )
    annex_cost = fields.Monetary(
        string="Annex Cost",
        currency_field="currency_id",
    )

    def unlink(self):
        for record in self:
            record.contract_id.contract_annex_amount -= 1
        return super(ContractAnnex, self).unlink()

    def create(self, values_list):
        if isinstance(values_list, dict):
            values_list = [values_list]
        for rec_data in values_list:
            if not rec_data.get("name"):
                rec_data["name"] = self._generate_annex_name(rec_data)
        records = super(ContractAnnex, self).create(values_list)
        for record in records:
            record.contract_id.contract_annex_amount += 1
            record.annex_number = record.contract_id.contract_annex_amount
            record._set_annex_to_invoice()
        return records

    def _generate_annex_name(self, data):
        """
        Generates default annex name from dict for record creation or from record itself.
        :param data: dict
        :return: str
        """
        # If annex_number in data, it is annex creation, and this number should be incremented by 1
        # Otherwise it is annex modifying, and annex_number remains the same.
        annex_number = (
            data["annex_number"] + 1
            if data.get("annex_number", "no_value") != "no_value"
            else self.annex_number
        )
        annex_date = (
            data["date_conclusion"]
            if data.get("date_conclusion")
            else self.date_conclusion
        )
        return (_("Annex №%s from %s", annex_number, annex_date),)

    def _set_annex_to_invoice(self):
        """
        For binding Invoice with Annex.
        Implemented in contract_account module, if it is installed.
        :return:
        """
        pass

    def action_open_annex_form(self):
        view_id = self.env.ref("contract.contract_annex_view_form").id
        context = self._context.copy()
        return {
            "name": _("Contact annex"),
            "view_type": "form",
            "view_mode": "tree",
            "views": [(view_id, "form")],
            "res_model": "contract.annex",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "target": "current",
            "context": context,
        }
