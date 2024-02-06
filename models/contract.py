import datetime
import logging
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError

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
    date_conclusion = fields.Date(
        string="Signing date in system",
        readonly=True,
    )
    commencement_date = fields.Date(
        string="Contract commencement date",
        help="Field for pointing out manually when contract was actually signed.",
        default=lambda self: self.date_conclusion,
        required=True,
    )
    contract_annex_ids = fields.One2many(
        comodel_name="contract.annex",
        inverse_name="contract_id",
        string="Annexes",
        help="Annexes to this contract",
    )
    contract_annex_amount = fields.Integer(default=0, help="Counter for tech purposes")

    section_ids = fields.One2many("contract.section", "contract_id", string="Sections")

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
        store=False,
    )
    responsible_employee_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible employee",
        domain=lambda self: [("groups_id", "=", self.env.ref("base.group_user").id)],
        default=lambda self: self.env.user,
    )
    expiration_date = fields.Date(string="Contract expiration date")
    notification_expiration = fields.Boolean(
        default=False,
        string="Contract expiration notice",
        help="Notify the responsible employee of the expiration of the contract",
    )
    notification_expiration_period = fields.Integer(
        default=1,
        string="Notice period, days",
        help="The day's number to contract expiration for sending notice",
    )
    renew_automatically = fields.Boolean(
        default=False, string="Renew contract automatically"
    )
    renew_period = fields.Integer(default=1, string="Contract renew period")
    renew_period_type = fields.Selection(
        [
            ("days", "Days"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        string="Type of contract renew period",
        default="days",
        required=True,
    )

    version_ids = fields.One2many(
        "contract.version",
        "contract_id",
        string="Versions",
        copy=False,
    )

    published_version_id = fields.Many2one(
        "contract.version", string="Published Version", readonly=True
    )

    published_version_number = fields.Integer(
        related="published_version_id.version_number",
        string="Published Version Number",
        readonly=True,
    )

    draft_version_ids = fields.One2many(
        "contract.version",
        "contract_id",
        string="Draft Versions",
        domain=[("is_published", "=", False)],
    )

    version_count = fields.Integer(
        string="Version Count", compute="_compute_version_count", store=False
    )

    signed_version_id = fields.Many2one(
        "contract.version", string="Signed Version", readonly=True
    )

    @api.depends("version_ids")
    def _compute_version_count(self):
        for record in self:
            record.version_count = len(record.version_ids)

    @api.model
    def create(self, vals):
        if self.env.context.get("copy") is not True:
            contract = super().create(vals)
            self.env["contract.version"].create(
                {
                    "contract_id": contract.id,
                    "version_number": 1,
                }
            )
            return contract
        else:
            return super().create(vals)

    def unlink(self):
        self.contract_annex_ids.unlink()
        return super(Contract, self).unlink()

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        if not self.published_version_id:
            raise UserError(_("Cannot duplicate without a published version."))
        default = dict(default or {})
        default.update({"published_version_id": False})
        new_contract = super(Contract, self.with_context(copy=True)).copy(default)
        current_version = self.published_version_id
        new_version = current_version.copy(
            {
                "contract_id": new_contract.id,
                "is_published": False,
                "version_number": 1,
            }
        )
        for section in current_version.section_ids:
            new_section = section.copy(
                {"contract_id": new_contract.id, "version_id": new_version.id}
            )
            for line in section.line_ids:
                new_line = line.copy(
                    {"section_id": new_section.id, "contract_id": new_contract.id}
                )
        return new_contract

    def get_allow_not_signed_contract(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        allow_not_signed_contract = ir_config.get_param(
            "contract.allow_not_signed_contract"
        )
        for record in self:
            record.allow_not_signed_contract = allow_not_signed_contract

    def create_new_version(self):
        self.ensure_one()

        if not self.published_version_id:
            raise UserError(_("Cannot create new version without a published version."))
        if self.state in ["sign", "close"]:
            raise UserError(
                _("Cannot create a new version of a signed or closed contract.")
            )

        return {
            "name": _("Create New Contract Version"),
            "type": "ir.actions.act_window",
            "res_model": "contract.version.creation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_contract_id": self.id,
            },
        }

    @api.constrains("section_ids")
    def _check_sign_version(self):
        for record in self:
            if record.state == "sign":
                raise UserError(
                    _("Cannot modify the content of a published contract version.")
                )

    def action_sign(self):
        return {
            "name": _("Sign Contract"),
            "type": "ir.actions.act_window",
            "res_model": "contract.version.sign.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_contract_id": self.id,
                "draft_version_ids": self.draft_version_ids.ids,
                "published_version_id": self.published_version_id.id,
            },
        }

    def action_unsign(self):
        if self.state != "sign":
            raise UserError(_("Cannot sign without a sign status."))
        self.signed_version_id.write({"is_signed": False})
        self.write(
            {"state": "draft", "date_conclusion": False, "signed_version_id": False}
        )

    def action_close(self):
        self.write({"state": "close"})

    def action_renew(self):
        self.write({"state": "draft"})

    def renew_contract(self):
        renew_period = {self.renew_period_type: self.renew_period}
        new_expiration_date = self.expiration_date + relativedelta(**renew_period)
        self.write({"expiration_date": new_expiration_date})

    def check_contracts(self):
        # Select active contracts
        contracts = self.search(
            [
                ("state", "=", "sign"),
            ]
        )
        try:
            template_name = "contract.contract_expiration_notification"
            template = self.env.ref(template_name)
        except ValueError:
            _logger.error('Template "%s" not found!', template_name)
        else:
            for contract in contracts:
                if contract._send_notification_today():
                    if contract.responsible_employee_id.notification_type == "email":
                        template.send_mail(contract.id)
        finally:
            for contract in contracts:
                if (
                    contract.renew_automatically
                    and contract.expiration_date == datetime.date.today()
                ):
                    contract.renew_contract()
                elif (
                    not contract.renew_automatically
                    and contract.expiration_date == datetime.date.today()
                ):
                    contract.action_close()

    def _send_notification_today(self):
        return (
            self.responsible_employee_id
            and self.notification_expiration
            and self.expiration_date
            and self.expiration_date
            - datetime.timedelta(days=self.notification_expiration_period)
            == datetime.date.today()
        )

    @api.constrains("notification_expiration_period")
    def _check_notification_expiration_period(self):
        for record in self:
            if (
                record.notification_expiration_period
                and record.notification_expiration_period <= 0
            ):
                raise models.ValidationError(
                    _(
                        "The validity period of the notification must be a positive number"
                    )
                )

    @api.constrains("renew_period")
    def _check_renew_period(self):
        for record in self:
            if record.renew_period and record.renew_period <= 0:
                raise models.ValidationError(
                    _("The contract new period must be a positive number")
                )

    def open_publish_wizard(self):
        if self.state == "sign":
            raise UserError(_("Cannot publish a new version of a signed contract."))
        return {
            "name": _("Publish Contract Version"),
            "view_mode": "form",
            "res_model": "contract.publish_wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_contract_id": self.id},
        }

    def show_versions(self):
        self.ensure_one()
        return {
            "name": _("Contract Versions"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "contract.version",
            "domain": [("contract_id", "=", self.id)],
            "context": {"default_contract_id": self.id},
            "target": "current",
        }
