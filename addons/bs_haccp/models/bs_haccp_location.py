from odoo import fields, models


class BsHaccpLocation(models.Model):
    _name = 'bs.haccp.location'
    _description = 'HACCP Location'
    _order = 'name'

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)