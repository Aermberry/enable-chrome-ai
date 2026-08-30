import json
import tempfile
import unittest
from pathlib import Path

from main import patch_local_state, set_glic_eligibility


class PatchLocalStateTest(unittest.TestCase):
    def test_creates_eligibility_for_each_profile(self):
        state = {'profile': {'info_cache': {'Default': {}, 'Work': {'is_glic_eligible': False}}}}

        self.assertTrue(set_glic_eligibility(state))
        self.assertTrue(state['profile']['info_cache']['Default']['is_glic_eligible'])
        self.assertTrue(state['profile']['info_cache']['Work']['is_glic_eligible'])

    def test_patches_chrome_152_style_state(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory, 'Local State')
            state_path.write_text(json.dumps({
                'glic': {'launcher_enabled': True},
                'profile': {'info_cache': {'Default': {'is_glic_eligible': False}}},
                'variations_country': 'us',
                'variations_permanent_consistency_country': ['152.0.7977.65', 'us'],
            }), encoding='utf-8')

            self.assertTrue(patch_local_state(directory, '152.0.7977.65'))
            patched = json.loads(state_path.read_text(encoding='utf-8'))
            self.assertTrue(patched['profile']['info_cache']['Default']['is_glic_eligible'])
            self.assertTrue(patched['glic']['launcher_enabled'])


if __name__ == '__main__':
    unittest.main()
