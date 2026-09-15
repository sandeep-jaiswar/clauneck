import pytest
from pydantic import ValidationError

from app.model import Quantity, Solver, SolverMethod, TimeSpan


def test_solver_settings_are_required():
    # timeSpan is now optional (required only for time-dependent problems)
    solver = Solver(method=SolverMethod.RK45, tolerance=1e-6)
    assert solver.timeSpan is None

    solver = Solver(
        method=SolverMethod.RK45,
        tolerance=1e-6,
        timeSpan=TimeSpan(start=0, end=1),
    )
    assert solver.timeSpan.end == 1


@pytest.mark.parametrize(
    ("value", "is_known"),
    [(1.0, False), (None, True)],
)
def test_quantity_known_status_must_match_value(value, is_known):
    with pytest.raises(ValidationError):
        Quantity(name="x", value=value, siUnit="m", isKnown=is_known)
