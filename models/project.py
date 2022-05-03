import logging
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    ready_state = fields.Boolean(default=False)