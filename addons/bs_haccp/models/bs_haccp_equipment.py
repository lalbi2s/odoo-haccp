from odoo import fields, models


class BsHaccpEquipment(models.Model):
    _name = 'bs.haccp.equipment'
    _description = 'HACCP Equipment'
    _order = 'name'

    name = fields.Char(required=True)
    brand = fields.Char()
    reference = fields.Char()
    serial_number = fields.Char()
    location_id = fields.Many2one('bs.haccp.location')
    equipment_type = fields.Selection([
        ('fridge', 'Fridge'),
        ('freezer', 'Freezer'),
    ], required=True)
    temp_min = fields.Float(string='Min Temperature (°C)', required=True)
    temp_max = fields.Float(string='Max Temperature (°C)', required=True)
    check_interval_hours = fields.Integer(
        string='Check Interval (hours)', required=True, default=12)
    active = fields.Boolean(default=True)