import logging
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    ready_state = fields.Boolean(default=False)



class CrmLeadTask(models.Model):
    _inherit = 'project.task'

    lead_id = fields.Many2one('crm.lead', tracking=True)
    quotation_ready = fields.Boolean(default=False)

    product_id = fields.Many2one(
        'product.product', 'Related product variant',
        check_company=True, index=True,
        domain="['&', '&', ('type', 'in', ['consu']),  ('product_tmpl_id', '=', product_tmpl_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="A product variant that is the related to this task")

    product_tmpl_id = fields.Many2one(
        'product.template', 'Related product template',
        check_company=True, index=True,
        domain="['&',('type', 'in', ['consu']),  '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="A product template that is the related to this task")        

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """Reset product_id or assign the first variant of the selected product_tmpl_id."""
        if self.product_tmpl_id:
            variants = self.product_tmpl_id.product_variant_ids
            # Reset product_id to the first variant if available, otherwise set to False
            self.product_id = variants and variants[0] or False
        else:
            self.product_id = False        