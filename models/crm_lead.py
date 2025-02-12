# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    task_ids = fields.One2many(
        'project.task', 'lead_id', string="Tasks", tracking=True)
    task_count = fields.Integer(
        compute='_compute_task_count')
    task_ready = fields.Boolean(
        compute='_compute_task_ready')


    client_ref = fields.Char("Client reference")

    @api.depends('task_ids')
    def _compute_task_ready(self):
        ready = True
        for record in self:
            for task in self.task_ids:
                _logger.info("Checking whether task is ready: %s : %s", task.name, task.stage_id.ready_state)
                if task.stage_id.ready_state == False:
                    ready = False
                    break
            if len(self.task_ids) == 0:
                ready = False
        self.task_ready = ready


    @api.depends('task_ids')
    def _compute_task_count(self):
        _logger.info("quickly counting the tasks")
        for record in self:
            record.task_count = len(record.task_ids)

    def action_view_tasks(self):
        self.ensure_one()

        list_view_id = self.env.ref('project.view_task_tree2').id
        form_view_id = self.env.ref('project.view_task_form2').id

        action = {'type': 'ir.actions.act_window_close'}
        task_project = int(self.env['ir.config_parameter'].sudo().get_param('jt_lead_task.default_projectid'))
        # _logger.info('default task project is %s', task_project)
        if len(self.task_ids) > 1:
            action = self.with_context(active_id=task_project).env['ir.actions.actions']._for_xml_id(
                'project.act_project_project_2_project_task_all')
            action['domain'] = [('id', 'in', self.task_ids.ids)]
            if action.get('context'):
                eval_context = self.env['ir.actions.actions']._get_eval_context(
                )
                eval_context.update({'active_id': task_project})
                action_context = safe_eval(action['context'], eval_context)
                action_context.update(eval_context)
                action['context'] = action_context
        else:
            action = self.env["ir.actions.actions"]._for_xml_id(
                "project.action_view_task")
            # erase default context to avoid default filter
            action['context'] = {}
            if len(self.task_ids) > 1:  # cross project kanban task
                action['views'] = [[False, 'kanban'], [list_view_id, 'list'], [
                    form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot']]
            elif len(self.task_ids) == 1:  # single task -> form view
                action['views'] = [(form_view_id, 'form')]
                action['res_id'] = self.task_ids.id
        # filter on the task of the current SO
        action.setdefault('context', {})
        action['context'].update({'search_default_lead_id': self.id})
        return action


    def action_sale_quotations_newer(self):
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            sale_order_vals = {
                'name': self.env['ir.sequence'].next_by_code('sale.order'),
                'partner_id': self.partner_id.id,
                'source_id': self.source_id.id,
                'opportunity_id': self.id,
                'tag_ids': [(6, 0, self.tag_ids.ids)],
                'company_id': self.company_id.id or self.env.company.id,
                'campaign_id': self.campaign_id.id,
                'origin': self.name,
                'client_order_ref': self.client_ref,
            }
            sale_order = self.env["sale.order"].create(sale_order_vals)

            dropship_route = self.env['stock.route'].search([('name', '=', 'Dropship')])

            for task in self.task_ids:
                product = task.product_id
                if product is not None:
                    order_line_vals = {
                        'name': product.display_name,
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'product_uom_qty': 1.0,
                    }

                    otf_bom_template = product.otf_bom_template
                    if otf_bom_template is not None and dropship_route is not None:
                        if otf_bom_template.dropship:
                            order_line_vals['route_id'] = dropship_route.id

                    order_line = self.env["sale.order.line"].create(order_line_vals)

            view = self.env.ref("sale.view_order_form")

            return {
                "name": "New Quotation",
                "view_mode": "form",
                "view_id": view.id,
                "res_model": "sale.order",
                "type": "ir.actions.act_window",
                "res_id": sale_order.id,
                "context": self.env.context,
            }        

    def action_new_quotation(self):
        action = super(CrmLead, self).action_new_quotation()
        action['context'].update({
            'default_client_order_ref': self.client_ref,
        })
        return action



