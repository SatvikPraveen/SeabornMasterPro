"""Execute every curriculum notebook end to end (opt-in: ``pytest -m notebooks``)."""

from __future__ import annotations

from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")
nbclient = pytest.importorskip("nbclient")

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS = sorted(NOTEBOOK_DIR.glob("*.ipynb"))


@pytest.mark.notebooks
@pytest.mark.slow
@pytest.mark.parametrize("path", NOTEBOOKS, ids=[p.stem for p in NOTEBOOKS])
def test_notebook_executes(path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    nb = nbformat.read(path, as_version=4)
    monkeypatch.chdir(NOTEBOOK_DIR)
    client = nbclient.NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        allow_errors=False,
        resources={"metadata": {"path": str(NOTEBOOK_DIR)}},
    )
    client.execute()
    n_code = sum(1 for c in nb.cells if c.cell_type == "code")
    assert n_code > 0
