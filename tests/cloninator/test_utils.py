import os
from pathlib import Path
from unittest import mock

import pytest

from cloninator import utils


@mock.patch("cloninator.utils.CONF", Path(os.devnull))
def test_get_repo_name() -> None:
    with pytest.raises(ValueError):
        utils.get_repos(Path())
