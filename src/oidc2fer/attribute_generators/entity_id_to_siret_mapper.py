import json
import logging

from satosa.micro_services.base import ResponseMicroService

logger = logging.getLogger(__name__)


class EntityIdToSiretMapper(ResponseMicroService):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attribute = config.get("attribute", "siret")
        self.mapping = json.loads(config.get("mapping_json", "{}"))

    def process(self, context, data):
        entity_id = data.auth_info.issuer
        if entity_id in self.mapping:
            siret = self.mapping[entity_id]
            logger.info("Mapping entity ID %s to SIRET %s", entity_id, siret)
            data.attributes[self.attribute] = siret
        else:
            logger.warning("No SIRET mapping found for entity ID %s", entity_id)
        return super().process(context, data)
