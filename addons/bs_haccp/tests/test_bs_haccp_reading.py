from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBsHaccpReading(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fridge = cls.env['bs.haccp.equipment'].create(
            {
                'name': 'Test Fridge',
                'equipment_type': 'fridge',
                'temp_min': 0.0,
                'temp_max': 4.0,
            }
        )

    def _create_reading(self, temperature, corrective_action=False):
        return self.env['bs.haccp.reading'].create(
            {
                'equipment_id': self.fridge.id,
                'temperature': temperature,
                'corrective_action': corrective_action,
            }
        )

    def test_is_compliant_inside_thresholds(self):
        self.assertTrue(self._create_reading(2.0).is_compliant)

    def test_is_compliant_on_thresholds(self):
        self.assertTrue(self._create_reading(0.0).is_compliant)
        self.assertTrue(self._create_reading(4.0).is_compliant)

    def test_is_compliant_outside_thresholds(self):
        too_hot = self._create_reading(9.0, 'Moved the food to another fridge.')
        too_cold = self._create_reading(-3.0, 'Raised the thermostat.')
        self.assertFalse(too_hot.is_compliant)
        self.assertFalse(too_cold.is_compliant)

    def test_is_compliant_follows_equipment_thresholds(self):
        reading = self._create_reading(3.0)
        self.fridge.temp_max = 2.0
        self.assertFalse(reading.is_compliant)

    def test_corrective_action_required_when_out_of_range(self):
        with self.assertRaises(ValidationError):
            self._create_reading(9.0)

    def test_corrective_action_cannot_be_blank(self):
        with self.assertRaises(ValidationError):
            self._create_reading(9.0, '   ')

    def test_corrective_action_not_required_when_compliant(self):
        reading = self._create_reading(2.0)
        self.assertFalse(reading.corrective_action)

    def test_corrective_action_checked_on_write(self):
        reading = self._create_reading(2.0)
        with self.assertRaises(ValidationError):
            reading.temperature = 9.0

    def test_corrective_action_cannot_be_removed(self):
        reading = self._create_reading(9.0, 'Called the technician.')
        with self.assertRaises(ValidationError):
            reading.corrective_action = False
