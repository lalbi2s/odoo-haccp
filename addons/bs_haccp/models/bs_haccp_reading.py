from odoo import fields, models


class BsHaccpReading(models.Model):
    _name = 'bs.haccp.reading'
    _description = 'HACCP Temperature Reading'
    _order = 'reading_date desc'

    reading_date = fields.Datetime(required=True, default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', required=True, default=lambda self: self.env.user)
    equipment_id = fields.Many2one(
        'bs.haccp.equipment', required=True, ondelete='restrict')
    temperature = fields.Float(string='Temperature (°C)', required=True)
    corrective_action = fields.Text()