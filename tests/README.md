# RemoteX Test Suite

## Running Tests

### Run all tests:
```bash
python tests/run_tests.py
```

### Run specific test file:
```bash
python -m unittest tests.test_ssh_config
python -m unittest tests.test_config
```

### Run with verbose output:
```bash
python -m unittest tests.test_ssh_config -v
```

## Test Structure

- `test_ssh_config.py` - SSH configuration management tests
- `test_config.py` - RemoteX configuration tests
- `run_tests.py` - Test runner script

## Adding New Tests

1. Create a new test file: `tests/test_<module>.py`
2. Import unittest and the module to test
3. Create test classes inheriting from `unittest.TestCase`
4. Add test methods starting with `test_`

Example:
```python
import unittest
from remotex.my_module import my_function

class TestMyModule(unittest.TestCase):
    def test_my_function(self):
        result = my_function("input")
        self.assertEqual(result, "expected")
```

## Test Coverage

To check test coverage (requires `coverage` package):
```bash
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report
```

