"""cfncli version."""

import pkg_resources

try:
  packages = pkg_resources.require('cfncli')
  __version__ = packages[0].version if packages else "0.0"
except pkg_resources.DistributionNotFound: ## local development
  __version__ = "0.0"
