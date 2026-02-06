import os
import importlib
from cryptography.fernet import Fernet
import pytest

# Use a deterministic env key so module doesn't attempt to write to home key file during import
TEST_KEY = Fernet.generate_key().decode()


@pytest.fixture(autouse=True)
def set_test_key_env(monkeypatch):
    monkeypatch.setenv("JALA_SHIELD_KEY", TEST_KEY)
    # Ensure module is reloaded each test to pick up env var
    if "jalaviveka" in globals():
        importlib.reload(globals()["jalaviveka"])
    yield
    # no cleanup required (env is patched)

def import_module():
    # Import/reload module after env var is set
    import importlib
    module = importlib.import_module("jalaviveka")
    importlib.reload(module)
    return module

def test_nikhilam_multiply_basic():
    jal = import_module()
    assert jal.nikhilam_multiply(98, 97, base=100) == 9506
    assert jal.nikhilam_multiply(100, 100, base=100) == 10000
    assert jal.nikhilam_multiply(95, 97, base=100) == 9215

def test_nikhilam_multiply_with_carry():
    jal = import_module()
    # 51 * 51 = 2601 -> right part exceeds base and creates carry
    assert jal.nikhilam_multiply(51, 51, base=100) == 2601

def test_evaluate_viveka_boundaries():
    jal = import_module()
    status, action = jal.evaluate_viveka({"flow_rate": 80})
    assert "SATTVIC" in status
    status, action = jal.evaluate_viveka({"flow_rate": 40})
    assert "RAJASIC" in status
    status, action = jal.evaluate_viveka({"flow_rate": 10})
    assert "TAMASIC" in status

def test_encrypt_decrypt_roundtrip():
    jal = import_module()
    msg = b"unit test message"
    token = jal.encrypt_report(msg)
    assert isinstance(token, (bytes, bytearray))
    out = jal.decrypt_report(token)
    assert out == msg