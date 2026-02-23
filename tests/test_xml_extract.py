import pytest

from trading.config import AppConfig
from trading.infra.anthropic_client import AnthropicRouter


def test_extract_execution_orders_array_only():
    router = AnthropicRouter(AppConfig(raw={}))
    text = "<execution_orders>[{\"a\":1}]</execution_orders>"
    assert router.extract_execution_orders(text) == [{"a": 1}]


def test_extract_execution_orders_reject_object():
    router = AnthropicRouter(AppConfig(raw={}))
    with pytest.raises(ValueError):
        router.extract_execution_orders("<execution_orders>{\"a\":1}</execution_orders>")
