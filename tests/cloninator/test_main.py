from unittest import mock

from cloninator.__main__ import main


@mock.patch(
    "cloninator.__main__.parse_args",
    new=mock.MagicMock(return_value=mock.MagicMock(subcommand="clone")),
)
@mock.patch("cloninator.__main__.clone")
def test_clone(mock_clone: mock.MagicMock) -> None:
    main()
    assert mock_clone.call_count == 1
    calls = [mock.call()]
    assert mock_clone.call_args_list == calls


@mock.patch(
    "cloninator.__main__.parse_args",
    new=mock.MagicMock(return_value=mock.MagicMock(subcommand="generate")),
)
@mock.patch("cloninator.__main__.generate")
def test_generate(mock_generate: mock.MagicMock) -> None:
    main()
    assert mock_generate.call_count == 1
    calls = [mock.call()]
    assert mock_generate.call_args_list == calls
