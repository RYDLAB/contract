from datetime import datetime


def migrate(cr, version):
    cr.execute(
        """DELETE FROM ir_model_fields WHERE model_id in (select id from ir_model WHERE model = 'contract.version.publish.wizard');
        DELETE FROM ir_model_relation WHERE model in (select id from ir_model WHERE model = 'contract.version.publish.wizard');
        DELETE FROM ir_model WHERE model = 'contract.version.publish.wizard';
        DROP TABLE IF EXISTS contract_version_publish_wizard cascade;"""
    )
