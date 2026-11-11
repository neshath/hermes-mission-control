import json, os, tempfile, unittest
from pathlib import Path
os.environ["HERMES_MISSION_CONTROL_DIR"] = tempfile.mkdtemp()
import __init__ as plugin
class TestPlugin(unittest.TestCase):
 def test_plan_and_status(self):
  out=json.loads(plugin._handle_plan({"goal":"Ship feature","steps":["Design","Test"]}))
  self.assertTrue(out["success"]); self.assertEqual(len(out["plan"]["steps"]),2)
  status=json.loads(plugin._handle_status({})); self.assertEqual(len(status["active_plans"]),1)
 def test_validation(self):
  self.assertFalse(json.loads(plugin._handle_plan({"goal":"","steps":[]}))["success"])
if __name__=="__main__": unittest.main()
