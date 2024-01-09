from datetime import datetime


def migrate(cr, version):
    cr.execute(
        "DELETE FROM ir_model WHERE model = 'contract.version.publish.wizard'"
    )
