from __future__ import annotations

import typer

from trading.main import implementation_plan, run_decision, run_schedule_probe
from trading.setup import maybe_run_setup_wizard, reset_setup

app = typer.Typer(no_args_is_help=True)


@app.command("setup")
def setup_cmd() -> None:
    maybe_run_setup_wizard()




@app.command("reset")
def reset_cmd() -> None:
    reset_setup()

@app.command("plan")
def plan_cmd() -> None:
    print(implementation_plan())


@app.command("run-decision")
def run_decision_cmd() -> None:
    maybe_run_setup_wizard()
    payload = run_decision()
    print({"keys": list(payload.keys())})


@app.command("run-schedule")
def run_schedule_cmd() -> None:
    run_schedule_probe()


if __name__ == "__main__":
    app()
