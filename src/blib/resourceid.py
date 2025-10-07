from dataclasses import dataclass
from enum import Enum

class ResourceIdType(Enum):
    doi = 1
    arxiv = 2

@dataclass
class ResourceId:
    id: str
    type: ResourceIdType