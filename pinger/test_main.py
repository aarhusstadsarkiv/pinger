import unittest
from unittest.mock import patch, mock_open
from unittest.mock import AsyncMock, patch

from main import read_config
from main import ping


class TestReadConfig(unittest.TestCase):
    def test_read_config(self):
        # Test case where config file exists and is valid
        with patch('builtins.open', mock_open(read_data='sites:\n  - name: Google\n    url: https://www.google.com\n    endpoint: /\n    expected_status: 200\ninterval: 30\ntimeout: 5\n')):
            config = read_config('config.yaml')
            self.assertEqual(config['interval'], 30)
            self.assertEqual(config['timeout'], 5)
            self.assertEqual(len(config['sites']), 1)
            self.assertEqual(config['sites'][0]['name'], 'Google')
            self.assertEqual(config['sites'][0]['url'], 'https://www.google.com')
            self.assertEqual(config['sites'][0]['endpoint'], '/')
            self.assertEqual(config['sites'][0]['expected_status'], 200)

        # Test case where config file does not exist
        with self.assertRaises(SystemExit) as cm:
            with patch('os.path.exists', return_value=False):
                read_config('config.yaml')
        self.assertEqual(cm.exception.code, 1)

        # Test case where config file is invalid
        with self.assertRaises(AssertionError):
            with patch('builtins.open', mock_open(read_data='sites:\n  - name: Google\n    url: https://www.google.com\n    endpoint: /\n')):
                read_config('config.yaml')
                



class TestPing(unittest.IsolatedAsyncioTestCase):
    async def test_ping_success(self):
        site = {
            "url": "https://www.google.com",
            "endpoint": "/",
            "expected_status": 200
        }
        response_mock = AsyncMock(status_code=200)
        client_mock = AsyncMock(get=AsyncMock(return_value=response_mock))

        with patch('main.client', client_mock):
            result = await ping(site)
            self.assertTrue(result)

    async def test_ping_failure(self):
        site = {
            "url": "https://www.google.com",
            "endpoint": "/",
            "expected_status": 200
        }
        response_mock = AsyncMock(status_code=404)
        client_mock = AsyncMock(get=AsyncMock(return_value=response_mock))

        with patch('main.client', client_mock):
            result = await ping(site)
            self.assertFalse(result)

    async def test_ping_exception(self):
        site = {
            "url": "https://www.google.com",
            "endpoint": "/",
            "expected_status": 200
        }
        client_mock = AsyncMock(get=AsyncMock(side_effect=Exception))

        with patch('main.client', client_mock):
            result = await ping(site)
            self.assertFalse(result)

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()