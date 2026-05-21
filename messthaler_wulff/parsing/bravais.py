from typing import Literal, Optional

import numpy as np
from pydantic import BaseModel

from messthaler_wulff.math.bravais import Bravais
from messthaler_wulff.parsing.common import VectorModel, list2vec


class BravaisModel(BaseModel):
    type: Literal["bravais"]
    primitives: list[VectorModel]
    transform: Optional[list[list[float]]] = None

    def bravais(self):
        if self.transform is None:
            transform = self.transform
        else:
            transform = np.array(self.transform)

        return Bravais(list(map(list2vec, self.primitives)), transform)
