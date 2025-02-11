import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class CrmLeadTaskWizard(models.TransientModel):
    _name = 'jt.lead.task.wizard'
    _description = 'Wizard to creat Lead Tasks'

    # @api.model
    # def default_get(self, fields):
    #     result = super().default_get(fields)
    #     lead_id = self.env.context.get("active_id")
    #     if lead_id:
    #         result["lead_id"] = lead_id
    #     return result

    def default_project_id(self):
        return self.env['ir.config_parameter'].sudo().get_param('jt_lead_task.default_projectid')


    lead_id = fields.Many2one(
        comodel_name="crm.lead", string="Lead", domain=[("type", "=", "lead")]
    )
    project_id = fields.Many2one(
        comodel_name="project.project", string="Project", default=default_project_id)

    def add_lead_task_and_go(self):
        _logger.info("add_lead_task_and_go - START - Wizard ID: %s, Lead ID: %s, Project ID: %s", self.id, self.lead_id.id if self.lead_id else None, self.project_id.id if self.project_id else None)
        task = self.add_lead_task()
        _logger.info("add_lead_task_and_go - Task created: %s", task.id if task else None)

        if task and task.project_id.otf_bom_template_id:
            _logger.info("add_lead_task_and_go - Found an otf bom template for task: %s", task.id)
            bom = task.project_id.otf_bom_template_id.create_otf_bom_product()
            product = bom.product_id
            #@TODO replace with commercial entity
            if task.partner_id.parent_id:
                product.partner_id = task.partner_id.parent_id
            else:
                product.partner_id = task.partner_id
            task.product_id = product
            product.task_id = task

            task_prefix = self.env['ir.config_parameter'].sudo().get_param('jt_lead_task.task_prefix')
            task_name = task_prefix + ' ' + product.code
            task.name = task_name

            note_subtype_id = self.env['ir.model.data']._xmlid_to_res_id(
                'mail.mt_note')

            product.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': product, 'origin': task.lead_id},
                subtype_id=note_subtype_id,
            )

        else:
            _logger.info("add_lead_task_and_go - No otf bom template found for task: %s", task.id if task else 'N/A')


        # return to task view
        view = self.env.ref("project.view_task_form2")
        _logger.info("add_lead_task_and_go - View is %s", view)
        _logger.info("add_lead_task_and_go - END - Returning action for task: %s", task.id if task else None)
        return {
            "name": "Task created",
            "view_mode": "form",
            "view_id": view.id,
            "res_model": "project.task",
            "type": "ir.actions.act_window",
            "res_id": task.id if task else None, # Handle case where task might not be created
            "context": self.env.context,
        }

 


    def add_lead_task(self):
        _logger.info("add_lead_task - START - Wizard ID: %s, Lead ID: %s, Project ID: %s", self.id, self.lead_id.id if self.lead_id else None, self.project_id.id if self.project_id else None)
        self.ensure_one()
        # get the lead to transform
        lead = self.lead_id
        _logger.info("add_lead_task - Lead: %s, Partner Name: %s, Contact Name: %s", lead.id if lead else None, lead.partner_name, lead.contact_name)
        partner = lead._find_matching_partner()
        _logger.info("add_lead_task - Matching Partner: %s", partner.id if partner else None)
        if not partner and (lead.partner_name or lead.contact_name):
            lead._handle_partner_assignment()
            partner = lead.partner_id
            _logger.info("add_lead_task - Partner Assigned: %s", partner.id if partner else None)

        # create new project.task
        task_prefix = self.env['ir.config_parameter'].sudo().get_param('jt_lead_task.task_prefix')
        task_name = task_prefix + ' ' + lead.name
        vals = {
            "name": task_name,
            "description": lead.description,
            # "email_from": lead.email_from,
            "project_id": self.project_id.id,
            "partner_id": partner.id if partner else None, # Handle case where partner might be None
            "user_ids": [(lead.user_id.id)],
            "lead_id": lead.id,
        }
        _logger.info("add_lead_task - Task vals: %s", vals)
        task = self.env["project.task"].create(vals)
        _logger.info("add_lead_task - Task created: %s", task.id if task else None)


        # add chatter
        body = 'Created from opportunity ' + lead.name
        task.message_post(
            body=body,
            message_type='notification'
        )
        body = 'Created task '
        lead.message_post(
            body=body,
            message_type='notification'
        )

        _logger.info("add_lead_task - END - Returning task: %s", task.id if task else None)
        return task



