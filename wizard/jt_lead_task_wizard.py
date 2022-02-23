import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class CrmLeadTaskWizard(models.TransientModel):
    _name = 'jt.lead.task.wizard'

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        lead_id = self.env.context.get("active_id")
        if lead_id:
            result["lead_id"] = lead_id
        return result

    def default_project_id(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('jt_lead_task.default_projectid'))


    lead_id = fields.Many2one(
        comodel_name="crm.lead", string="Lead", domain=[("type", "=", "lead")]
    )
    project_id = fields.Many2one(
        comodel_name="project.project", string="Project", default=default_project_id)

    def add_lead_task(self):
        _logger.info("about to add a lead task from wizard")
        self.ensure_one()
        # get the lead to transform
        lead = self.lead_id
        partner = lead._find_matching_partner()
        if not partner and (lead.partner_name or lead.contact_name):
            lead._handle_partner_assignment()
            partner = lead.partner_id
        # create new project.task
        task_prefix = self.env['ir.config_parameter'].sudo().get_param('jt_lead_task.task_prefix')
        task_name = task_prefix + ' ' + lead.name
        vals = {
            "name": task_name,
            "description": lead.description,
            "email_from": lead.email_from,
            "project_id": self.project_id.id,
            "partner_id": partner.id,
            "user_ids": [(lead.user_id.id)],
            "lead_id": lead.id,
        }
        task = self.env["project.task"].create(vals)

        # add chatter
        body = 'Created from lead ' + lead.name
        task.message_post(
            body=body,
            message_type='notification'
        )
        body = 'Created task '
        lead.message_post(
            body=body,
            message_type='notification'
        )

        # return to task view
        view = self.env.ref("project.view_task_form2")
        _logger.info("View is %s", view)
        return {
            "name": "Task created",
            "view_mode": "form",
            "view_id": view.id,
            "res_model": "project.task",
            "type": "ir.actions.act_window",
            "res_id": task.id,
            "context": self.env.context,
        }
