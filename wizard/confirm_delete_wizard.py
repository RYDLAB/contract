from odoo import api, fields, models

class ConfirmDeletionWizard(models.TransientModel):
    _name = 'confirm.deletion.wizard'
    _description = 'Confirm Deletion Wizard'

    confirm_message = fields.Char(
        string='Confirmation Message',
        readonly=True,
        default='Are you sure you want to delete?'
    )

    def button_confirm_deletion(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        record_to_delete = self.env[self.env.context.get('active_model')].browse(active_id)
        record_to_delete.unlink()
        return {'type': 'ir.actions.act_window_close'}