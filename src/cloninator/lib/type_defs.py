from typing import TypedDict, Union

from typing_extensions import Required  # upgrade: py3.10: import from typing


class RemoteData(TypedDict):
    name: str
    url: str


RepoData = TypedDict(
    "RepoData",
    {"/remotes": Required[list[RemoteData]], "/post_checkout": list[str]},
    total=False,
)

DirectoryData = dict[str, Union[RepoData, "DirectoryData"]]
