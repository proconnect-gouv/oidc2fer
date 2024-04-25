from satosa.internal import InternalData

from oidc2fer.attribute_processors.flattening_processor import FlatteningProcessor


class TestFlatteningProcessor:
    def test_flattens_values(self):
        processor = FlatteningProcessor()
        internal_data = InternalData()
        internal_data.attributes = {"name": ["Albert", "Betty"]}
        processor.process(internal_data, "name")
        assert internal_data.attributes["name"] == "Albert Betty"

    def test_ignores_missing_attribute(self):
        processor = FlatteningProcessor()
        internal_data = InternalData()
        internal_data.attributes = {}
        processor.process(internal_data, "name")
        assert internal_data.attributes == {}

    def test_leaves_string_alone(self):
        processor = FlatteningProcessor()
        internal_data = InternalData()
        internal_data.attributes = {"name": "AlreadyFlat"}
        processor.process(internal_data, "name")
        assert internal_data.attributes["name"] == "AlreadyFlat"
