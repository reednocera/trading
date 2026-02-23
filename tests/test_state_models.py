import pytest

sqlalchemy = pytest.importorskip("sqlalchemy")

from trading.state.models import Attribution, PortfolioState, Position


def test_state_models_have_expected_tables():
    assert PortfolioState.__tablename__ == "portfolio_state"
    assert Position.__tablename__ == "positions"
    assert Attribution.__tablename__ == "attribution"
