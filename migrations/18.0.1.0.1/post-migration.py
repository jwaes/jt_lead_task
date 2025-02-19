import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    env = util.env(cr)
    # Search for all project.task records with a product_id set
    tasks = env['project.task'].search([('product_id', '!=', False)])
    for task in tasks:
        # Set the new field product_tmpl_id to the product template of the product variant
        task.product_tmpl_id = task.product_id.product_tmpl_id.id
