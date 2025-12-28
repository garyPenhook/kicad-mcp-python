import pytest

pytest.importorskip("mcp", reason="mcp dependency not installed")
pytest.importorskip("kipy", reason="kipy (kicad-python) not installed")

from kicad_mcp_python.server import create_server


def test_create_server():
    server = create_server()
    assert server is not None
    assert hasattr(server, 'run')
    assert callable(server.run)
