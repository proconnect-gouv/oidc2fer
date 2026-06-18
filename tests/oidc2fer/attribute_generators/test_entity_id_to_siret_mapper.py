import json

from satosa.context import Context
from satosa.internal import AuthenticationInformation, InternalData

from oidc2fer.attribute_generators import EntityIdToSiretMapper


class TestEntityIdToSiretMapper:
    def create_mapper(self):
        mapper = EntityIdToSiretMapper(
            config={
                "attribute": "siret",
                "mapping_json": json.dumps(
                    {
                        "https://idp.example.fr": "12345678200010",
                    }
                ),
            },
            name="siret_mapper",
            base_url="https://satosa.example.com",
        )
        mapper.next = lambda ctx, data: data
        return mapper

    def test_sets_siret_for_known_entityid(self):
        mapper = self.create_mapper()
        resp = InternalData(
            auth_info=AuthenticationInformation(issuer="https://idp.example.fr")
        )
        ctx = Context()
        mapper.process(ctx, resp)
        assert resp.attributes["siret"] == "12345678200010"

    def test_does_not_set_siret_for_unknown_entityid(self):
        mapper = self.create_mapper()
        resp = InternalData(
            auth_info=AuthenticationInformation(issuer="https://unknown.example.fr")
        )
        ctx = Context()
        mapper.process(ctx, resp)
        assert "siret" not in resp.attributes
