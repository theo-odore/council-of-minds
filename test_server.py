import requests
import time
import subprocess
import sys
import unittest

SERVER_URL = "http://localhost:5000"

class TestCouncilServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start server in background
        cls.server_process = subprocess.Popen([sys.executable, "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Waiting for server to start...")
        time.sleep(5) # Give it time to start

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_01_get_philosophers(self):
        try:
            r = requests.get(f"{SERVER_URL}/philosophers")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertIn('socrates', data)
            self.assertIn('model', data['socrates'])
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to server")

    def test_02_update_model(self):
        # Change Socrates model to 'mistral'
        new_model = "mistral:latest"
        r = requests.put(f"{SERVER_URL}/philosophers/socrates/model", json={"model": new_model})
        self.assertEqual(r.status_code, 200)
        
        # Verify
        r = requests.get(f"{SERVER_URL}/philosophers")
        data = r.json()
        self.assertEqual(data['socrates']['model'], new_model)

    def test_03_create_session(self):
        r = requests.post(f"{SERVER_URL}/sessions")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('id', data)
        self.session_id = data['id']

if __name__ == '__main__':
    unittest.main()
