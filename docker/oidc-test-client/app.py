from flask import Flask, jsonify, request, session
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic import rndstr
from oic.oic.message import Claims, ClaimsRequest, RegistrationResponse
from oic.utils.http_util import Redirect
from oic.oic.message import AuthorizationResponse
from werkzeug.exceptions import InternalServerError
import secrets
import logging
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = Flask(__name__)
app.config.update(
    {
        "SECRET_KEY": secrets.token_hex(
            10
        ),  # random key so that sessions don't survive restarts
    }
)


def create_client() -> Client:
    client = Client(client_authn_method=CLIENT_AUTHN_METHOD)

    client.provider_config(os.environ["OIDC_PROVIDER"])

    info = {
        "client_id": os.environ["OIDC_CLIENT_ID"],
        "client_secret": os.environ["OIDC_CLIENT_SECRET"],
    }
    client.store_registration_info(RegistrationResponse(**info))

    client.redirect_uris = [f"{os.environ['OIDC_ROOT_URL']}/redirect_uri"]

    return client


@app.route("/")
def index():
    client = create_client()

    session["state"] = rndstr()
    session["nonce"] = rndstr()

    auth_req = client.construct_AuthorizationRequest(
        request_args={
            "client_id": client.client_id,
            "response_type": "code",
            "scope": os.environ["OIDC_SCOPES"].split(","),
            "nonce": session["nonce"],
            "redirect_uri": client.redirect_uris[0],
            "state": session["state"],
            "claims": ClaimsRequest(id_token=Claims(acr=None, amr=None)),
        }
    )
    login_url = auth_req.request(client.authorization_endpoint)

    return Redirect(login_url)


@app.route("/redirect_uri")
def oidc_callback():
    client = create_client()

    response = request.query_string.decode("utf-8")
    aresp = client.parse_response(
        AuthorizationResponse, info=response, sformat="urlencoded"
    )

    assert aresp["state"] == session["state"]

    if "error" in aresp:
        return jsonify(
            error_response=aresp.to_dict(),
        )

    code = aresp["code"]
    logging.info("got auth code=%s", code)

    access_token_response = client.do_access_token_request(
        state=aresp["state"],
        request_args={"code": aresp["code"]},
        authn_method="client_secret_post",
    )

    access_token = access_token_response["access_token"]
    logging.info("got access_token=%s", access_token)

    # userinfo = client.do_user_info_request(state=aresp["state"])
    userinfo = client.do_user_info_request(access_token=access_token)

    logging.info("got userinfo=%s", userinfo)

    return jsonify(
        access_token_response=access_token_response.to_dict(),
        userinfo=userinfo.to_dict(),
    )


@app.errorhandler(InternalServerError)
def handle_server_exception(e):
    exc = e.original_exception
    import traceback

    return (
        f"""<h1>Internal Server Error</h1>
        <pre>{"".join(traceback.format_exception(exc))}</pre>""",
        500,
    )


@app.route("/healthz")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0")
