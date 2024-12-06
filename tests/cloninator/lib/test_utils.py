import os
from pathlib import Path
from unittest import mock

import pytest

from cloninator.lib import utils


@mock.patch("cloninator.lib.utils.CONF", Path(os.devnull))
def test_get_repo_name() -> None:
    with pytest.raises(ValueError, match="Cannot infer type of"):
        utils.get_repos(Path())
