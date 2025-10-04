import os

# Read the TEST_MODE environment variable. Defaults to False if not set.
TEST_MODE = os.getenv('TEST_MODE', 'False').lower() == 'true'