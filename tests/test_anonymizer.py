"""Unit tests for intelliquery.chains.anonymizer output schema."""

from intelliquery.chains.anonymizer import AnonymizeOutput


class TestAnonymizeOutput:
    def test_schema_creation(self):
        output = AnonymizeOutput(
            anonymized_question="Why did PERSON_1 go to LOCATION_1?",
            entity_map={"PERSON_1": "Paul Atreides", "LOCATION_1": "Arrakis"},
        )
        assert output.anonymized_question == "Why did PERSON_1 go to LOCATION_1?"
        assert output.entity_map["PERSON_1"] == "Paul Atreides"
        assert output.entity_map["LOCATION_1"] == "Arrakis"

    def test_schema_serialisation(self):
        output = AnonymizeOutput(
            anonymized_question="What is ENTITY_1?",
            entity_map={"ENTITY_1": "Spice Melange"},
        )
        data = output.model_dump()
        assert isinstance(data, dict)
        assert "anonymized_question" in data
        assert "entity_map" in data
