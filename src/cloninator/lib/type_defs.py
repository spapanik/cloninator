from typing import Required, TypedDict, Union


class RemoteData(TypedDict):
    name: str
    url: str


RepoData = TypedDict(
    "RepoData",
    {"/remotes": Required[list[RemoteData]], "/post_checkout": list[str]},
    total=False,
)

DirectoryData = dict[str, Union[RepoData, "DirectoryData"]]
