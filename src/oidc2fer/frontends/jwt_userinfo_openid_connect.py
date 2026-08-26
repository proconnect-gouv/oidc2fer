import logging
from urllib.parse import urlencode

from oic.oic.message import UserInfoErrorResponse
from pyop.access_token import AccessToken
from pyop.exceptions import BearerTokenError, InvalidAccessToken
from satosa.frontends.openid_connect import OpenIDConnectFrontend
from satosa.response import Response, Unauthorized

logger = logging.getLogger(__name__)


class JWTUserInfoOpenIDConnectFrontend(OpenIDConnectFrontend):
    def userinfo_endpoint(self, context):
        headers = {"Authorization": context.request_authorization}

        try:
            response = self.provider.handle_userinfo_request(
                request=urlencode(context.request),
                http_headers=headers,
            )
            return Response(
                response.to_jwt([self.signing_key], self.signing_key.alg),
                content="application/jwt",
            )
        except (BearerTokenError, InvalidAccessToken) as e:
            error_resp = UserInfoErrorResponse(
                error="invalid_token", error_description=str(e)
            )
            response = Unauthorized(
                error_resp.to_json(),
                headers=[("WWW-Authenticate", AccessToken.BEARER_TOKEN_TYPE)],
                content="application/json",
            )
            return response
