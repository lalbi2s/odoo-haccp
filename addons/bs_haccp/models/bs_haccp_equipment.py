from datetime import timedelta

from odoo import api, fields, models


class BsHaccpEquipment(models.Model):
    _name = 'bs.haccp.equipment'
    _description = 'HACCP Equipment'
    _order = 'name'

    name = fields.Char(required=True)
    brand = fields.Char()
    reference = fields.Char()
    serial_number = fields.Char()
    location_id = fields.Many2one('bs.haccp.location')
    equipment_type = fields.Selection(
        [
            ('fridge', 'Fridge'),
            ('freezer', 'Freezer'),
        ],
        required=True,
    )
    temp_min = fields.Float(string='Min Temperature (°C)', required=True)
    temp_max = fields.Float(string='Max Temperature (°C)', required=True)
    check_interval_hours = fields.Integer(
        string='Check Interval (hours)', required=True, default=12
    )
    reading_ids = fields.One2many('bs.haccp.reading', 'equipment_id')
    last_reading_date = fields.Datetime(
        compute='_compute_last_reading_date', store=True
    )
    check_state = fields.Selection(
        [
            ('up_to_date', 'Up to Date'),
            ('due_soon', 'Due Soon'),
            ('overdue', 'Overdue'),
        ],
        compute='_compute_check_state',
    )
    active = fields.Boolean(default=True)

    _temp_range_check = models.Constraint(
        'CHECK(temp_min < temp_max)',
        'The minimum temperature must be lower than the maximum temperature.',
    )

    @api.depends('reading_ids.reading_date')
    def _compute_last_reading_date(self):
        for equipment in self:
            dates = equipment.reading_ids.mapped('reading_date')
            equipment.last_reading_date = max(dates) if dates else False

    @api.depends('last_reading_date', 'check_interval_hours')
    def _compute_check_state(self):
        now = fields.Datetime.now()
        for equipment in self:
            if not equipment.last_reading_date:
                equipment.check_state = 'overdue'
                continue
            next_reading = equipment.last_reading_date + timedelta(
                hours=equipment.check_interval_hours
            )
            if now > next_reading:
                equipment.check_state = 'overdue'
            elif next_reading - now < timedelta(hours=1):
                equipment.check_state = 'due_soon'
            else:
                equipment.check_state = 'up_to_date'
