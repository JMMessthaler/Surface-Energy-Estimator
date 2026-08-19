from pathlib import Path

from pydantic import RootModel

from messthaler_wulff.parsing.common import NodeModel, list2vec, vec2list
from messthaler_wulff.utils import duplicates


class CrystalModel(RootModel):
    root: list[NodeModel]


def from_json(json: str) -> list:
    model = CrystalModel.model_validate_json(json)

    values = list(map(list2vec, model.root))
    dupl = duplicates(values)
    if len(dupl) > 0:
        raise ValueError(f"Duplicate vector in crystal: {", ".join(map(str, dupl))}")
    return values


def to_json(x: list) -> str:
    model = CrystalModel(list(map(vec2list, x)))
    return model.model_dump_json()


def from_path(path: Path):
    path = Path(path)
    if path == Path("-"):
        string = input("Enter crystal json here: ")
    else:
        assert path.exists()  # TODO
        string = path.read_text()

    return from_json(string)
