# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import api, fields, models, _


class FSMOrder(models.Model):
    _inherit = 'maintenance.request'
    _description = 'Field Service Order'

    # Request
    tag_ids = fields.Many2many('fsm.tag', 'fsm_order_tag_rel',
                               'fsm_order_id',
                               'tag_id', string='Tags',
                               help="Classify and analyze your orders")
    customer_id = fields.Many2one('res.partner', string='Customer',
                                  domain=[('customer', '=', True)],
                                  change_default=True,
                                  index=True,
                                  track_visibility='always')
    fsm_location_id = fields.Many2one('fsm.location', string='Location',
                                      index=True)
    origin = fields.Char(string='Origin')

    # Planning
    fsm_person_id = fields.Many2one('fsm.person',
                                    string='Assigned To',
                                    index=True)
    fsm_route_id = fields.Many2one('fsm.route', string='Route', index=True)
    scheduled_date_start = fields.Datetime(string='Scheduled Start')
    scheduled_duration = fields.Float(string='Duration in hours',
                                      help='Scheduled duration of the work in'
                                           ' hours')
    scheduled_date_end = fields.Datetime(string="Scheduled End")
    sequence = fields.Integer(string='Sequence', default=10)
    todo = fields.Text(string='Instructions')

    # Execution
    log = fields.Text(string='Log')
    date_start = fields.Datetime(string='Actual Start')
    date_end = fields.Datetime(string='Actual End')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_next = self.env['ir.sequence'].next_by_code
            vals['name'] = seq_next('maintenance.request') or _('New')
        return super(FSMOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'scheduled_date_end' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_end')) -\
                timedelta(hours=self.scheduled_duration)
            vals['scheduled_date_start'] = str(date_to_with_delta)
        if 'scheduled_duration' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_start', self.scheduled_date_start)) +\
                timedelta(hours=vals.get('scheduled_duration'))
            vals['scheduled_date_end'] = str(date_to_with_delta)
        if 'scheduled_date_end' not in vals and 'scheduled_date_start' in vals:
            date_to_with_delta = fields.Datetime.from_string(
                vals.get('scheduled_date_start')) +\
                timedelta(hours=self.scheduled_duration)
            vals['scheduled_date_end'] = str(date_to_with_delta)
        return super(FSMOrder, self).write(vals)

    def action_confirm(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_confirmed').id})

    def action_schedule(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_scheduled').id})

    def action_assign(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_assigned').id})

    def action_plan(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_planned').id})

    def action_enroute(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_enroute').id})

    def action_start(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_started').id})

    def action_complete(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_completed').id})

    def action_cancel(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_cancelled').id})

    @api.onchange('scheduled_date_end')
    def onchange_scheduled_date_end(self):
        if self.scheduled_date_end:
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_end) -\
                timedelta(hours=self.scheduled_duration)
            self.date_start = str(date_to_with_delta)

    @api.onchange('scheduled_duration')
    def onchange_scheduled_duration(self):
        if self.scheduled_duration:
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_start) +\
                timedelta(hours=self.scheduled_duration)
            self.scheduled_date_end = str(date_to_with_delta)
