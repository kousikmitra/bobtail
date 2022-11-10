from abc import ABC, abstractmethod
from typing import List, Tuple

from bobtail.response import Response
from bobtail.request import Request


class AbstractRoute(ABC):

    @abstractmethod
    def get(self, req: Request, res: Response) -> None:
        pass

    @abstractmethod
    def post(self, req: Request, res: Response) -> None:
        pass

    @abstractmethod
    def put(self, req: Request, res: Response) -> None:
        pass

    @abstractmethod
    def delete(self, req: Request, res: Response) -> None:
        pass


TypeRoute = Tuple[AbstractRoute, str]
