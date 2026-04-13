import sys
import os
import pytest
from mutmut.runner import Runner
from mutmut.__main__ import Config

# Simulating mutmut's baseline run
# We need to set PYTEST_ADDOPTS here because mutmut reads it via os.environ in pytest.main()
os.environ['PYTEST_ADDOPTS'] = '-p no:django -p no:sugar .'

config = Config(
    paths_to_mutate=['src/'],
    pytest_add_cli_args_test_selection='.',
    runner='python -m pytest',
)
runner = Runner(config=config)
try:
    print('Starting run_stats...')
    ec = runner.run_stats()
    print(f'Stats exit code: {ec}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
