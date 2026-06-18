from satosa.exception import SATOSAAuthenticationError
from satosa.micro_services.base import ResponseMicroService


class AffiliationCheckError(SATOSAAuthenticationError):
    def __init__(self, state, message):
        super().__init__(state, message)
        # Override SATOSAAuthenticationError's _message property to keep the custom message
        self._message = message + " Error id [{error_id}]"


class AffiliationChecker(ResponseMicroService):
    def __init__(self, config, *args, **kwargs):
        self.attribute_name = config.get("attribute_name", "eduPersonAffiliation")
        self.allowed_values = set(config.get("allowed_values", []))
        super().__init__(*args, **kwargs)

    def process(self, context, data):
        if self.attribute_name not in data.attributes:
            raise AffiliationCheckError(
                context.state, f"L'attribut {self.attribute_name} est manquant"
            )
        values = data.attributes[self.attribute_name]
        if not any(v.lower() in self.allowed_values for v in values):
            raise AffiliationCheckError(
                context.state,
                f"Aucune des valeurs pour {self.attribute_name} n'est autorisée: {values}",
            )
        return super().process(context, data)
