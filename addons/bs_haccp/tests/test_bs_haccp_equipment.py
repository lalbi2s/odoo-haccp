from datetime import datetime, timedelta

from freezegun import freeze_time
from psycopg2 import IntegrityError

from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger

NOW = datetime(2026, 10, 13, 12, 0, 0)


@tagged('post_install', '-at_install')
class TestBsHaccpEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fridge = cls.env['bs.haccp.equipment'].create(
            {
                'name': 'Test Fridge',
                'equipment_type': 'fridge',
                'temp_min': 0.0,
                'temp_max': 4.0,
                'check_interval_hours': 12,
            }
        )

    def _create_reading(self, hours_ago):
        return self.env['bs.haccp.reading'].create(
            {
                'equipment_id': self.fridge.id,
                'temperature': 2.0,
                'reading_date': NOW - timedelta(hours=hours_ago),
            }
        )

    @freeze_time(NOW)
    def test_check_state_no_reading(self):
        self.assertFalse(self.fridge.last_reading_date)
        self.assertEqual(self.fridge.check_state, 'overdue')

    @freeze_time(NOW)
    def test_check_state_up_to_date(self):
        self._create_reading(hours_ago=2)
        self.assertEqual(self.fridge.check_state, 'up_to_date')

    @freeze_time(NOW)
    def test_check_state_due_soon(self):
        # Next check is in 30 minutes: less than one hour left.
        self._create_reading(hours_ago=11.5)
        self.assertEqual(self.fridge.check_state, 'due_soon')

    @freeze_time(NOW)
    def test_check_state_overdue(self):
        self._create_reading(hours_ago=13)
        self.assertEqual(self.fridge.check_state, 'overdue')

    @freeze_time(NOW)
    def test_check_state_uses_last_reading(self):
        self._create_reading(hours_ago=30)
        last_reading = self._create_reading(hours_ago=1)
        self.assertEqual(self.fridge.last_reading_date, last_reading.reading_date)
        self.assertEqual(self.fridge.check_state, 'up_to_date')

    @mute_logger('odoo.sql_db')
    def test_temp_min_must_be_lower_than_temp_max(self):
        with self.assertRaises(IntegrityError):
            self.fridge.write({'temp_min': 5.0})
            self.env.flush_all()

    @mute_logger('odoo.sql_db')
    def test_temp_min_cannot_equal_temp_max(self):
        with self.assertRaises(IntegrityError):
            self.env['bs.haccp.equipment'].create(
                {
                    'name': 'Wrong Freezer',
                    'equipment_type': 'freezer',
                    'temp_min': -18.0,
                    'temp_max': -18.0,
                }
            )
