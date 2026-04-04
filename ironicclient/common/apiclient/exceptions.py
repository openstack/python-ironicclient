# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 Nebula, Inc.
# Copyright 2013 Alessio Ababilov
# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Exception definitions.
"""

from __future__ import annotations

from http import client as http_client
import inspect
import sys
from typing import Any, cast

import requests

from ironicclient.common.i18n import _


class ClientException(Exception):
    """The base exception class for all exceptions this library raises."""
    pass


class ValidationError(ClientException):
    """Error in validation on API client side."""
    pass


class UnsupportedVersion(ClientException):
    """User is trying to use an unsupported version of the API."""
    pass


class CommandError(ClientException):
    """Error in CLI tool."""
    pass


class AuthorizationFailure(ClientException):
    """Cannot authorize API client."""
    pass


class ConnectionError(ClientException):
    """Cannot connect to API service."""
    pass


class ConnectionRefused(ConnectionError):
    """Connection refused while trying to connect to API service."""
    pass


class AuthPluginOptionsMissing(AuthorizationFailure):
    """Auth plugin misses some options."""
    def __init__(self, opt_names: list[str]) -> None:
        super(AuthPluginOptionsMissing, self).__init__(
            _("Authentication failed. Missing options: %s") %
            ", ".join(opt_names))
        self.opt_names = opt_names


class AuthSystemNotFound(AuthorizationFailure):
    """User has specified an AuthSystem that is not installed."""
    def __init__(self, auth_system: str) -> None:
        super(AuthSystemNotFound, self).__init__(
            _("AuthSystemNotFound: %r") % auth_system)
        self.auth_system = auth_system


class NoUniqueMatch(ClientException):
    """Multiple entities found instead of one."""
    pass


class EndpointException(ClientException):
    """Something is rotten in Service Catalog."""
    pass


class EndpointNotFound(EndpointException):
    """Could not find requested endpoint in Service Catalog."""
    pass


class AmbiguousEndpoints(EndpointException):
    """Found more than one matching endpoint in Service Catalog."""
    def __init__(self, endpoints: object | None = None) -> None:
        super(AmbiguousEndpoints, self).__init__(
            _("AmbiguousEndpoints: %r") % endpoints)
        self.endpoints = endpoints


class HttpError(ClientException):
    """The base exception class for all HTTP exceptions."""
    http_status: int = 0
    message: str = _("HTTP Error")

    def __init__(
        self,
        message: str | None = None,
        details: str | None = None,
        response: requests.Response | None = None,
        request_id: str | None = None,
        url: str | None = None,
        method: str | None = None,
        http_status: int | None = None,
    ) -> None:
        self.http_status = http_status or self.http_status
        self.message = message or self.message
        self.details = details
        self.request_id = request_id
        self.response = response
        self.url = url
        self.method = method
        formatted_string = "%s (HTTP %s)" % (self.message, self.http_status)
        if request_id:
            formatted_string += " (Request-ID: %s)" % request_id
        super(HttpError, self).__init__(formatted_string)


class HTTPRedirection(HttpError):
    """HTTP Redirection."""
    message: str = _("HTTP Redirection")


class HTTPClientError(HttpError):
    """Client-side HTTP error.

    Exception for cases in which the client seems to have erred.
    """
    message: str = _("HTTP Client Error")


class HttpServerError(HttpError):
    """Server-side HTTP error.

    Exception for cases in which the server is aware that it has
    erred or is incapable of performing the request.
    """
    message: str = _("HTTP Server Error")


class MultipleChoices(HTTPRedirection):
    """HTTP 300 - Multiple Choices.

    Indicates multiple options for the resource that the client may follow.
    """

    http_status: int = http_client.MULTIPLE_CHOICES
    message: str = _("Multiple Choices")


class BadRequest(HTTPClientError):
    """HTTP 400 - Bad Request.

    The request cannot be fulfilled due to bad syntax.
    """
    http_status: int = http_client.BAD_REQUEST
    message: str = _("Bad Request")


class Unauthorized(HTTPClientError):
    """HTTP 401 - Unauthorized.

    Similar to 403 Forbidden, but specifically for use when authentication
    is required and has failed or has not yet been provided.
    """
    http_status: int = http_client.UNAUTHORIZED
    message: str = _("Unauthorized")


class PaymentRequired(HTTPClientError):
    """HTTP 402 - Payment Required.

    Reserved for future use.
    """
    http_status: int = http_client.PAYMENT_REQUIRED
    message: str = _("Payment Required")


class Forbidden(HTTPClientError):
    """HTTP 403 - Forbidden.

    The request was a valid request, but the server is refusing to respond
    to it.
    """
    http_status: int = http_client.FORBIDDEN
    message: str = _("Forbidden")


class NotFound(HTTPClientError):
    """HTTP 404 - Not Found.

    The requested resource could not be found but may be available again
    in the future.
    """
    http_status: int = http_client.NOT_FOUND
    message: str = _("Not Found")


class MethodNotAllowed(HTTPClientError):
    """HTTP 405 - Method Not Allowed.

    A request was made of a resource using a request method not supported
    by that resource.
    """
    http_status: int = http_client.METHOD_NOT_ALLOWED
    message: str = _("Method Not Allowed")


class NotAcceptable(HTTPClientError):
    """HTTP 406 - Not Acceptable.

    The requested resource is only capable of generating content not
    acceptable according to the Accept headers sent in the request.
    """
    http_status: int = http_client.NOT_ACCEPTABLE
    message: str = _("Not Acceptable")


class ProxyAuthenticationRequired(HTTPClientError):
    """HTTP 407 - Proxy Authentication Required.

    The client must first authenticate itself with the proxy.
    """
    http_status: int = http_client.PROXY_AUTHENTICATION_REQUIRED
    message: str = _("Proxy Authentication Required")


class RequestTimeout(HTTPClientError):
    """HTTP 408 - Request Timeout.

    The server timed out waiting for the request.
    """
    http_status: int = http_client.REQUEST_TIMEOUT
    message: str = _("Request Timeout")


class Conflict(HTTPClientError):
    """HTTP 409 - Conflict.

    Indicates that the request could not be processed because of conflict
    in the request, such as an edit conflict.
    """
    http_status: int = http_client.CONFLICT
    message: str = _("Conflict")


class Gone(HTTPClientError):
    """HTTP 410 - Gone.

    Indicates that the resource requested is no longer available and will
    not be available again.
    """
    http_status: int = http_client.GONE
    message: str = _("Gone")


class LengthRequired(HTTPClientError):
    """HTTP 411 - Length Required.

    The request did not specify the length of its content, which is
    required by the requested resource.
    """
    http_status: int = http_client.LENGTH_REQUIRED
    message: str = _("Length Required")


class PreconditionFailed(HTTPClientError):
    """HTTP 412 - Precondition Failed.

    The server does not meet one of the preconditions that the requester
    put on the request.
    """
    http_status: int = http_client.PRECONDITION_FAILED
    message: str = _("Precondition Failed")


class RequestEntityTooLarge(HTTPClientError):
    """HTTP 413 - Request Entity Too Large.

    The request is larger than the server is willing or able to process.
    """
    http_status: int = http_client.REQUEST_ENTITY_TOO_LARGE
    message: str = _("Request Entity Too Large")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        try:
            self.retry_after = int(kwargs.pop('retry_after'))
        except (KeyError, ValueError):
            self.retry_after = 0

        super(RequestEntityTooLarge, self).__init__(*args, **kwargs)


class RequestUriTooLong(HTTPClientError):
    """HTTP 414 - Request-URI Too Long.

    The URI provided was too long for the server to process.
    """
    http_status: int = http_client.REQUEST_URI_TOO_LONG
    message: str = _("Request-URI Too Long")


class UnsupportedMediaType(HTTPClientError):
    """HTTP 415 - Unsupported Media Type.

    The request entity has a media type which the server or resource does
    not support.
    """
    http_status: int = http_client.UNSUPPORTED_MEDIA_TYPE
    message: str = _("Unsupported Media Type")


class RequestedRangeNotSatisfiable(HTTPClientError):
    """HTTP 416 - Requested Range Not Satisfiable.

    The client has asked for a portion of the file, but the server cannot
    supply that portion.
    """
    http_status: int = http_client.REQUESTED_RANGE_NOT_SATISFIABLE
    message: str = _("Requested Range Not Satisfiable")


class ExpectationFailed(HTTPClientError):
    """HTTP 417 - Expectation Failed.

    The server cannot meet the requirements of the Expect request-header field.
    """
    http_status: int = http_client.EXPECTATION_FAILED
    message: str = _("Expectation Failed")


class UnprocessableEntity(HTTPClientError):
    """HTTP 422 - Unprocessable Entity.

    The request was well-formed but was unable to be followed due to semantic
    errors.
    """
    http_status: int = http_client.UNPROCESSABLE_ENTITY
    message: str = _("Unprocessable Entity")


class InternalServerError(HttpServerError):
    """HTTP 500 - Internal Server Error.

    A generic error message, given when no more specific message is suitable.
    """
    http_status: int = http_client.INTERNAL_SERVER_ERROR
    message: str = _("Internal Server Error")


# NotImplemented is a python keyword.
class HttpNotImplemented(HttpServerError):
    """HTTP 501 - Not Implemented.

    The server either does not recognize the request method, or it lacks
    the ability to fulfill the request.
    """
    http_status: int = http_client.NOT_IMPLEMENTED
    message: str = _("Not Implemented")


class BadGateway(HttpServerError):
    """HTTP 502 - Bad Gateway.

    The server was acting as a gateway or proxy and received an invalid
    response from the upstream server.
    """
    http_status: int = http_client.BAD_GATEWAY
    message: str = _("Bad Gateway")


class ServiceUnavailable(HttpServerError):
    """HTTP 503 - Service Unavailable.

    The server is currently unavailable.
    """
    http_status: int = http_client.SERVICE_UNAVAILABLE
    message: str = _("Service Unavailable")


class GatewayTimeout(HttpServerError):
    """HTTP 504 - Gateway Timeout.

    The server was acting as a gateway or proxy and did not receive a timely
    response from the upstream server.
    """
    http_status: int = http_client.GATEWAY_TIMEOUT
    message: str = _("Gateway Timeout")


class HttpVersionNotSupported(HttpServerError):
    """HTTP 505 - HttpVersion Not Supported.

    The server does not support the HTTP protocol version used in the request.
    """
    http_status: int = http_client.HTTP_VERSION_NOT_SUPPORTED
    message: str = _("HTTP Version Not Supported")


# _code_map contains all the classes that have http_status attribute.
_code_map: dict[int, type[HttpError]] = {
    cast(int, getattr(obj, 'http_status')): cast(type[HttpError], obj)
    for name, obj in vars(sys.modules[__name__]).items()
    if inspect.isclass(obj) and getattr(obj, 'http_status', False)
}


def from_response(
    response: requests.Response, method: str, url: str
) -> HttpError:
    """Returns an instance of :class:`HttpError` or subclass based on response.

    :param response: instance of `requests.Response` class
    :param method: HTTP method used for request
    :param url: URL used for request
    """

    req_id = response.headers.get("x-openstack-request-id")
    # NOTE(hdd) true for older versions of nova and cinder
    if not req_id:
        req_id = response.headers.get("x-compute-request-id")
    kwargs: dict[str, Any] = {
        "http_status": response.status_code,
        "response": response,
        "method": method,
        "url": url,
        "request_id": req_id,
    }
    if "retry-after" in response.headers:
        kwargs["retry_after"] = response.headers["retry-after"]

    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("application/json"):
        try:
            body = response.json()
        except ValueError:
            pass
        else:
            if isinstance(body, dict):
                error = body.get(list(body)[0])
                if isinstance(error, dict):
                    kwargs["message"] = (error.get("message")
                                         or error.get("faultstring"))
                    kwargs["details"] = (error.get("details")
                                         or str(body))
    elif content_type.startswith("text/"):
        kwargs["details"] = getattr(response, 'text', '')

    cls: type[HttpError]
    try:
        cls = _code_map[response.status_code]
    except KeyError:
        # 5XX status codes are server errors
        if response.status_code >= http_client.INTERNAL_SERVER_ERROR:
            cls = HttpServerError
        # 4XX status codes are client request errors
        elif (http_client.BAD_REQUEST <= response.status_code
              < http_client.INTERNAL_SERVER_ERROR):
            cls = HTTPClientError
        else:
            cls = HttpError
    return cls(**kwargs)
