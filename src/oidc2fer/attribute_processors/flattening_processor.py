import logging

from satosa.micro_services.processors.base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class FlatteningProcessor(BaseProcessor):
    def __init__(self):
        pass

    # There's a bug in BaseProcessor, the 'self' argument is missing!
    # pylint: disable-next=arguments-differ
    def process(self, internal_data, attribute, **kwargs):
        attributes = internal_data.attributes
        if attribute in attributes:
            values = attributes.get(attribute)
            if isinstance(values, list):
                new_value = " ".join(values)
                logger.debug("flattening %s into %s", values, new_value)
                attributes[attribute] = new_value
