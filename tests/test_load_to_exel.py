import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
from load_to_exel import analyze_conversation, CallAnalysis

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

@patch("load_to_exel.client")  
def test_analyze_conversation_success(mock_client):
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "job_type": "Комп'ютерна діагностика",
        "manager_rating": 5,
        "is_ok": True,
        "comment": "Все чудово."
    })
    
    mock_client.models.generate_content.return_value = mock_response

    services_list = ["Слюсарні роботи", "Комп'ютерна діагностика"]
    result = analyze_conversation("Текст транскрибації", services_list)

    assert result["job_type"] == "Комп'ютерна діагностика"
    assert result["manager_rating"] == 5
    assert result["is_ok"] is True
    assert mock_client.models.generate_content.call_count == 1