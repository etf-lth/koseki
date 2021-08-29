
import logging
from typing import Union

from flask import Blueprint, jsonify, redirect, render_template, request
from jwkest.jwk import RSAKey, rsa_load
from oic.oic.message import (AuthorizationRequest, TokenErrorResponse,
                             UserInfoErrorResponse)
from pyop.access_token import AccessToken
from pyop.authz_state import AuthorizationState
from pyop.exceptions import (BearerTokenError, InvalidAccessToken,
                             InvalidAuthenticationRequest,
                             InvalidClientAuthentication, OAuthError)
from pyop.provider import Provider
from pyop.subject_identifier import HashBasedSubjectIdentifierFactory
from pyop.userinfo import Userinfo
from pyop.util import should_fragment_encode
from werkzeug.wrappers import Response

from koseki.db.storage import PersonWrapper, SQLWrapper
from koseki.db.types import Person
from koseki.plugin import KosekiPlugin

from koseki.util import KosekiAlert, KosekiAlertType


class OIDCPlugin(KosekiPlugin):
    def config(self) -> dict:
        return {}

    def plugin_enable(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.signing_key = RSAKey(key=rsa_load(
            "signing_key.pem"), use="sig", alg="RS256")
        # pylint: disable=attribute-defined-outside-init
        self.oidc_configuration_information = {
            "issuer": self.app.config["URL_BASE"].replace("http://", "https://"),
            "authorization_endpoint": self.app.config["URL_BASE"] + "/oidc/authorization",
            "jwks_uri": self.app.config["URL_BASE"] + "/oidc/jwks",
            "token_endpoint": self.app.config["URL_BASE"] + "/oidc/token",
            "userinfo_endpoint": self.app.config["URL_BASE"] + "/oidc/userinfo",
            "response_types_supported": ["code"],
            "id_token_signing_alg_values_supported": [self.signing_key.alg],
            "response_modes_supported": ["fragment", "query"],
            "subject_types_supported": ["public", "pairwise"],
            "grant_types_supported": ["authorization_code", "implicit"],
            "claim_types_supported": ["normal"],
            "claims_parameter_supported": True,
            "claims_supported": ["sub", "name", "given_name", "family_name", "email", "profile"],
            "scopes_supported": ["openid", "email", "profile"]
        }
        subject_id_factory = HashBasedSubjectIdentifierFactory(
            self.app.config["SECRET_KEY"])
        # pylint: disable=attribute-defined-outside-init
        self.provider = Provider(self.signing_key, self.oidc_configuration_information,
                                 AuthorizationState(
                                     subject_id_factory,
                                     SQLWrapper(self.storage, 'authz_codes'),
                                     SQLWrapper(self.storage, 'access_tokens'),
                                     SQLWrapper(
                                         self.storage, 'refresh_tokens'),
                                     SQLWrapper(
                                         self.storage, 'subject_identifiers', True),
                                 ),
                                 SQLWrapper(self.storage, 'clients'),
                                 Userinfo(PersonWrapper(self.storage)))

    def create_blueprint(self) -> Blueprint:
        blueprint: Blueprint = Blueprint(
            "oidc", __name__, template_folder="./templates")
        blueprint.add_url_rule(
            "/.well-known/openid-configuration", None, self.oidc_config, methods=["GET"])
        blueprint.add_url_rule(
            "/oidc/jwks", None, self.oidc_jwks, methods=["GET"])
        blueprint.add_url_rule("/oidc/authorization", None,
                               self.auth.require_session(
                                   self.oidc_authorization, None),
                               methods=["GET"])
        blueprint.add_url_rule("/oidc/token", None,
                               self.oidc_token, methods=["GET", "POST"])
        blueprint.add_url_rule("/oidc/userinfo", None,
                               self.oidc_userinfo, methods=["GET", "POST"])
        return blueprint

    def oidc_config(self) -> Union[str, Response]:
        return Response(self.provider.provider_configuration.to_json(), mimetype="application/json")

    def oidc_jwks(self) -> Union[str, Response]:
        return jsonify(self.provider.jwks)

    # require_session
    def oidc_authorization(self) -> Union[str, Response]:
        person: Person = self.storage.session.query(
            Person).filter_by(uid=self.util.current_user()).scalar()
        if person.state != "active":
            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.DANGER,
                    "Missing membership!",
                    "OpenID Connect login was successful, but active " +
                    "membership is required to log in to 3rd party services.",
                )
            )
            return render_template("oidc.html")

        try:
            # Override claims to always only and at least return email for CF
            authn_req = AuthorizationRequest().from_dict({**request.args, "claims": {
                "id_token": {
                    "email": {
                        "essential": True
                    }
                }
            }})
            logging.debug(authn_req)
            authn_req.verify()
            if authn_req["client_id"] not in self.provider.clients:
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Invalid Client",
                        "Unknown Client ID. All applications must be pre-registered.",
                    )
                )
                return render_template("oidc.html")
            client = self.provider.clients[authn_req["client_id"]]
            if client["redirect_uri"] != authn_req["redirect_uri"]:
                self.util.alert(
                    KosekiAlert(
                        KosekiAlertType.DANGER,
                        "Incorrect Redirect URI",
                        "Unauthorized redirect URI for this client.",
                    )
                )
                return render_template("oidc.html")

            authn_response = self.provider.authorize(
                authn_req, self.util.current_user())
            return_url = authn_response.request(
                authn_req["redirect_uri"], should_fragment_encode(authn_req))
            return redirect(return_url)
        except Exception as err:  # pylint: disable=broad-except
            self.util.alert(
                KosekiAlert(
                    KosekiAlertType.DANGER,
                    "OIDC Error",
                    "Error: {}".format(str(err)),
                )
            )
            return render_template("oidc.html")

    def oidc_token(self) -> Union[str, Response]:
        print(request)
        try:
            token_response = self.provider.handle_token_request(request.get_data().decode("utf-8"),
                                                                request.headers)
            return Response(token_response.to_json(), mimetype="application/json")
        except InvalidClientAuthentication as err:
            error_resp = TokenErrorResponse(
                error="invalid_client", error_description=str(err))
            http_response = Response(
                error_resp.to_json(), status=401, mimetype="application/json")
            http_response.headers["WWW-Authenticate"] = "Basic"
            logging.error(error_resp.to_dict())
            return http_response
        except OAuthError as err:
            error_resp = TokenErrorResponse(
                error=err.oauth_error, error_description=str(err))
            return Response(error_resp.to_json(), status=400, mimetype="application/json")

    def oidc_userinfo(self) -> Union[str, Response]:
        try:
            response = self.provider.handle_userinfo_request(request.get_data().decode("utf-8"),
                                                             request.headers)
            return Response(response.to_json(), mimetype="application/json")
        except (BearerTokenError, InvalidAccessToken) as err:
            error_resp = UserInfoErrorResponse(
                error="invalid_token", error_description=str(err))
            http_response = Response(
                error_resp.to_json(), status=401, mimetype="application/json")
            http_response.headers["WWW-Authenticate"] = AccessToken.BEARER_TOKEN_TYPE
            logging.error(error_resp.to_dict())
            return http_response
