from abc import ABC, abstractmethod
from typing import Any


# Define an abstract class
class BaseResponseMapper(ABC):
    @abstractmethod
    def transform_to_response(self, obj: Any):
        pass

    @abstractmethod
    def map_list_to_response(self, objs: list[Any]):
        pass
