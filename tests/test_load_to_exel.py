import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
from load_to_exel import CallAnalysis

def test_call_analysis_pydantic_schema():
    data = {
        "job_type": "Слюсарні роботи",
        "manager_rating": 4,
        "is_ok": True,
        "comment": "Менеджер був ввічливим."
    }
    model = CallAnalysis(**data)
    assert model.job_type == "Слюсарні роботи"
    assert model.manager_rating == 4
    assert model.is_ok is True