from typing import List, Tuple, Dict, Optional
from abc import ABC, abstractmethod
import json

from bobtail.response import Response
from bobtail.request import Request


class AbstractRoute(ABC):

    @abstractmethod
    def get(self, req: Request, res: Response) -> Tuple[Optional[Dict], int]:
        pass

    @abstractmethod
    def post(self, req: Request, res: Response) -> Tuple[Optional[Dict], int]:
        pass

    @abstractmethod
    def put(self, req: Request, res: Response) -> Tuple[Optional[Dict], int]:
        pass

    @abstractmethod
    def delete(self, req: Request, res: Response) -> Tuple[Optional[Dict], int]:
        pass


class NoRoutesError(Exception):
    pass


class RouteClassError(Exception):
    pass


class BobTail:

    environ: Dict

    routes: List[Tuple[AbstractRoute, str]]

    response: Response

    request: Request

    def _handle_404(self) -> Tuple[Optional[Dict], int]:
        return None, 404

    def __init__(self, *args, **kwargs):
        if "routes" not in kwargs:
            raise NoRoutesError("Expected a list of routes")
        self.routes = kwargs["routes"]

    def init_response(self):
        self.response = Response()

    def set_request(self):
        self.request = Request(
            path=self.environ["PATH_INFO"],
            method=self.environ["REQUEST_METHOD"],
        )

    def _call_handler(self, route: callable, method: str):
        if hasattr(route,  method):
            try:
                result = getattr(route, method)(self.request, self.response)
                if result is not None and len(result) == 2:
                    return result
                return None, 200
            except TypeError as exc:
                raise RouteClassError("route class is not instantiated") from exc
        else:
            return self._handle_404()

    def _handle_route(self) -> Tuple[Optional[Dict], int]:
        for current_route in self.routes:
            route, curr_path = current_route
            if curr_path == self.request.path:
                match self.request.method:
                    case "GET":
                        res = self._call_handler(route, "get")
                        return res
                    case "POST":
                        return self._call_handler(route, "post")
                    case "DELETE":
                        return self._call_handler(route, "delete")
                    case "PUT":
                        return self._call_handler(route, "put")
                    case "PATCH":
                        return self._call_handler(route, "patch")
        return None, 0

    def __call__(self, environ, start_response):
        self.environ = environ
        # Set request & response
        self.set_request()
        self.init_response()
        # Call route handler with default response
        self._handle_route()

        status = f"{self.response.status} OK"

        response_headers = [("Content-type", "application/json")]

        # Start response
        start_response(status, response_headers)
        # Process the final byte list & headers
        data = self.response._process()
        return data
