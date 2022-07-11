import datetime
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _name = "contract.contract"
    _description = "Contract"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    def _get_default_name(self):
        """Returns name format `№YYMM-D-N`,
        where N is a sequence number of contracts which are created this day
        """
        today = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        contracts_today = self.search([("create_date", ">=", today)])
        contract_date = "{format_date}-{number}".format(
            format_date=datetime.date.strftime(datetime.date.today(), "%y%m-%d"),
            number=len(contracts_today) + 1,
        )
        return contract_date

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        default=lambda self: self.env.context.get("active_id"),
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Contract's currency",
        help="Contract settlements should be performed in this currency.",
        default=lambda self: self.env.company.currency_id.id,
    )
    res_model = fields.Char(default=lambda self: self._name)
    name = fields.Char(
        string="Contract number",
        default=lambda self: self._get_default_name(),
        readonly=False,
    )
    type = fields.Selection(
        selection=[
            ("with_customer", "With customer"),
            ("with_vendor", "With vendor"),
        ],
        string="Contract type",
        help="Different relations requires different contracts with own text and template.",
        required=True,
    )
    create_date = fields.Datetime(string="Created on")
    date_conclusion = fields.Date(
        string="Signing date in system",
    )
    date_conclusion_fix = fields.Date(
        string="Actual signing date",
        help="Field for pointing out manually when contract was actually signed.",
        default=lambda self: self.date_conclusion,
    )
    contract_annex_ids = fields.One2many(
        comodel_name="contract.annex",
        inverse_name="contract_id",
        string="Annexes",
        help="Annexes to this contract",
    )
    contract_annex_amount = fields.Integer(default=0, help="Counter for tech purposes")
    state = fields.Selection(
        [
            ("draft", "New"),
            ("sign", "Signed"),
            ("close", "Closed"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        tracking=True,
        track_sequence=3,
        default="draft",
    )
    allow_not_signed_contract = fields.Boolean(
        compute="get_allow_not_signed_contract",
        default=lambda self: self.get_allow_not_signed_contract(),
        store=False,
    )
    responsible_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Responsible employee"
    )
    expiration_date = fields.Date(
        default=fields.Date.today() + datetime.timedelta(days=30),
        string="Contract expiration date"
    )
    notification_expiration = fields.Boolean(
        default=False,
        string="Contract expiration notice",
        help="Notify the responsible employee of the expiration of the contract"
    )
    notification_expiration_period = fields.Integer(
        default=1,
        string="Notice period, days",
        help="The number of days before the notification is received"
    )
    renew_automatically = fields.Boolean(default=False, string="Renew contract automatically")
    renew_period = fields.Integer(default=1, string="Contract renew period")
    renew_period_type = fields.Selection(
        [
            ("days", "Days"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        string="Type of contract renew period",
        required=True,
        default="days"
    )

    def unlink(self):
        self.contract_annex_ids.unlink()
        return super(Contract, self).unlink()

    def get_allow_not_signed_contract(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        allow_not_signed_contract = ir_config.get_param(
            "contract.allow_not_signed_contract"
        )
        self.write({"allow_not_signed_contract": allow_not_signed_contract})
        return allow_not_signed_contract

    def action_sign(self):
        self.write({"state": "sign", "date_conclusion": fields.Date.today()})

    def action_close(self):
        self.write({"state": "close"})

    def action_renew(self):
        self.write({"state": "draft"})

    @api.constrains('notification_expiration_period')
    def _check_notification_expiration_period(self):
        for record in self:
            if record.notification_expiration_period and record.notification_expiration_period <= 0:
                raise models.ValidationError('The validity period of the notification must be a positive number')

    @api.constrains('renew_period')
    def _check_renew_period(self):
        for record in self:
            if record.renew_period and record.renew_period <= 0:
                raise models.ValidationError('The contract new period must be a positive number')
