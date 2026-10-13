from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BsHaccpReading(models.Model):
    _name = 'bs.haccp.reading'
    _description = 'HACCP Temperature Reading'
    _order = 'reading_date desc'
    _rec_names_search = ('equipment_id.name',)

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

    @api.depends('equipment_id.name', 'reading_date')
    @api.depends_context('tz')
    def _compute_display_name(self):
        for reading in self:
            if not reading.equipment_id or not reading.reading_date:
                reading.display_name = reading.equipment_id.name or ''
                continue
            local_date = fields.Datetime.context_timestamp(
                reading, reading.reading_date
            )
            reading.display_name = (
                f'{reading.equipment_id.name} - {local_date:%Y-%m-%d %H:%M}'
            )

    @api.constrains('temperature', 'equipment_id', 'corrective_action')
    def _check_corrective_action(self):
        for reading in self:
            if (
                not reading.is_compliant
                and not (reading.corrective_action or '').strip()
            ):
                raise ValidationError(
                    self.env._(
                        'This reading is out of range: describe the corrective action.'
                    )
                )
