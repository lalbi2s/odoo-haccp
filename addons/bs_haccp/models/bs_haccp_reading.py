from odoo import api, fields, models


class BsHaccpReading(models.Model):
    _name = 'bs.haccp.reading'
    _description = 'HACCP Temperature Reading'
    _order = 'reading_date desc'

    reading_date = fields.Datetime(required=True, default=fields.Datetime.now)
    user_id = fields.Many2one(
        'res.users', required=True, default=lambda self: self.env.user
    )
    equipment_id = fields.Many2one(
        'bs.haccp.equipment', required=True, ondelete='restrict'
    )
    temperature = fields.Float(string='Temperature (°C)', required=True)
    is_compliant = fields.Boolean(compute='_compute_is_compliant', store=True)
    corrective_action = fields.Text()

    @api.depends('temperature', 'equipment_id.temp_min', 'equipment_id.temp_max')
    def _compute_is_compliant(self):
        for reading in self:
            equipment = reading.equipment_id
            reading.is_compliant = (
                equipment.temp_min <= reading.temperature <= equipment.temp_max
            )
