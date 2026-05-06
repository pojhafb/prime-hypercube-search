from __future__ import annotations

from abc import ABC, abstractmethod

from primecube.core.models import SearchResult


class SearchPolicy(ABC):
    name: str

    @abstractmethod
    def search(self, x: int, m: int) -> SearchResult:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
