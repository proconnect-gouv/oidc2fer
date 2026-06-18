import pytest
from satosa.context import Context
from satosa.exception import SATOSAAuthenticationError
from satosa.internal import AuthenticationInformation, InternalData

from oidc2fer.authorization import AffiliationChecker


class TestAffiliationChecker:
    def create_affiliation_checker(self):
        affiliation_checker = AffiliationChecker(
            config={
                "attribute_name": "eduPersonAffiliation",
                "allowed_values": ["employee"],
            },
            name="test_affiliation_checker",
            base_url="https://satosa.example.com",
        )
        affiliation_checker.next = lambda ctx, data: data
        return affiliation_checker

    def test_allows_expected_value(self):
        authz_service = self.create_affiliation_checker()
        resp = InternalData(auth_info=AuthenticationInformation())
        resp.attributes = {
            "eduPersonAffiliation": ["member", "employee"],
        }
        ctx = Context()
        ctx.state = {}
        authz_service.process(ctx, resp)

    def test_case_insensitive_match(self):
        authz_service = self.create_affiliation_checker()
        resp = InternalData(auth_info=AuthenticationInformation())
        resp.attributes = {
            "eduPersonAffiliation": ["EmpLoyEe"],
        }
        ctx = Context()
        ctx.state = {}
        authz_service.process(ctx, resp)

    def test_fail_when_attribute_missing(self):
        authz_service = self.create_affiliation_checker()
        resp = InternalData(auth_info=AuthenticationInformation())
        resp.attributes = {}
        with pytest.raises(
            SATOSAAuthenticationError,
            match="L'attribut eduPersonAffiliation est manquant",
        ):
            ctx = Context()
            ctx.state = {}
            authz_service.process(ctx, resp)

    def test_fail_when_no_allowed_values(self):
        authz_service = self.create_affiliation_checker()
        resp = InternalData(auth_info=AuthenticationInformation())
        resp.attributes = {
            "eduPersonAffiliation": ["student"],
        }
        with pytest.raises(
            SATOSAAuthenticationError,
            match=r"Aucune des valeurs pour eduPersonAffiliation n'est autorisée: \['student'\]",
        ):
            ctx = Context()
            ctx.state = {}
            authz_service.process(ctx, resp)
