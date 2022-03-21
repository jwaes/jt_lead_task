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
        compute='_compute_task_count', string="Task Count")

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
                action['views'] = [[False, 'kanban'], [list_view_id, 'tree'], [
                    form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot']]
            elif len(self.task_ids) == 1:  # single task -> form view
                action['views'] = [(form_view_id, 'form')]
                action['res_id'] = self.task_ids.id
        # filter on the task of the current SO
        action.setdefault('context', {})
        action['context'].update({'search_default_lead_id': self.id})
        return action

class CrmLeadTask(models.Model):
    _inherit = 'project.task'

    lead_id = fields.Many2one('crm.lead', tracking=True)

    product_id = fields.Many2one(
        'product.product', 'Related product',
        check_company=True, index=True,
        domain="['&',('type', 'in', ['product']),  '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="A product that is the related to this task")