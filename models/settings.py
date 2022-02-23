from odoo import models, fields, api

class CrmLeadTaskSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    project_id = fields.Many2one(
        'project.project', string="Default lead project", config_parameter='jt_lead_task.default_projectid')

    task_prefix = fields.Char('Task prefix', config_parameter='jt_lead_task.task_prefix')