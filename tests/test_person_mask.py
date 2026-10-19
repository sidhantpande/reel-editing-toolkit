import importlib.util,sys,unittest
from pathlib import Path

try:
 import numpy as np
 import scipy
except ImportError:
 np=None

@unittest.skipIf(np is None,'Run with the pinned clinic Python for mask tests')
class PersonMaskTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  folder=Path(__file__).resolve().parents[1]/'workspaces/my-dental-skin-clinic/tools'
  sys.path.insert(0,str(folder))
  spec=importlib.util.spec_from_file_location('subject_layers',folder/'subject_layers.py')
  cls.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)
 def test_background_balloon_removed_soft_hair_retained(self):
  mask=np.zeros((100,100),dtype=np.uint8)
  mask[35:95,15:85]=255
  mask[34,16:84]=80
  mask[8:25,65:82]=110
  cleaned=self.module.clean_person_mask(mask)
  self.assertEqual(int(cleaned[15,70]),0)
  self.assertEqual(int(cleaned[34,40]),80)
  self.assertEqual(int(cleaned[60,40]),255)
 def test_thin_wire_does_not_connect_balloon_to_presenter(self):
  mask=np.zeros((100,100),dtype=np.uint8)
  mask[40:95,15:85]=255;mask[5:20,65:80]=200;mask[20:41,72]=200
  cleaned=self.module.clean_person_mask(mask)
  self.assertEqual(int(cleaned[10,72]),0)
  self.assertEqual(int(cleaned[70,40]),255)
 def test_no_presenter_rejected(self):
  with self.assertRaisesRegex(ValueError,'No reliable presenter'):self.module.clean_person_mask(np.zeros((20,20),dtype=np.uint8))

if __name__=='__main__':unittest.main()
