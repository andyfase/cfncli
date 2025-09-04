# Development Guide

## Building from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/andyfase/cfncli.git
   cd cfncli
   ```

2. Install development dependencies:
   ```bash
   make setup
   ```

3. Install in development mode:
   ```bash
   make dev-install
   ```

4. Build the package:
   ```bash
   make build
   ```

## Available Make Targets

- `make setup` - Install development dependencies
- `make dev-install` - Install package in development mode
- `make build` - Build source and wheel distributions
- `make clean` - Remove build artifacts
- `make format` - Format code with Black
- `make lint` - Lint code
- `make test` - Run tests
- `make upload` - Upload to PyPI

## Development Workflow

1. Make your changes
2. Format code: `make format`
3. Run tests: `make test`
4. Build package: `make build`
5. Test installation: `make dev-install`

## Testing

The test suite uses `moto` to mock AWS services for comprehensive CLI testing without requiring actual AWS resources.

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=cfncli --cov-report=html

# Run specific test file
pytest tests/test_stack_deploy.py

# Run specific test
pytest tests/test_stack_deploy.py::test_stack_deploy_success
```

### Test Structure

- `tests/test_stack_deploy.py` - Deploy command tests
- `tests/test_stack_update.py` - Update command tests  
- `tests/test_stack_delete.py` - Delete command tests
- `tests/test_changeset.py` - Changeset create tests
- `tests/test_status.py` - Status command tests
- `tests/test_drift.py` - Drift detection tests
- `tests/test_validate.py` - Template validation tests
- `tests/test_generate.py` - Config generation tests

### Adding New Tests

1. Create test file following naming convention `test_*.py`
2. Import required moto decorators (`@mock_cloudformation`, `@mock_s3`, `@mock_sts`)
3. Use fixtures from `conftest.py`
4. Test both success and error scenarios
5. Verify CLI output and exit codes