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