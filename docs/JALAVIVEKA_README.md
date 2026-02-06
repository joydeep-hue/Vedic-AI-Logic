# JALA-VIVEKA — Local Run & Test Notes

This document explains how to run the project locally and how to run the unit tests added for the JALA-VIVEKA script.

## Environment & Fernet key

For local development you can provide a Fernet key through an environment variable:

- Environment variable: JALA_SHIELD_KEY

Generate a key with Python:
```bash
python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
```

Then export it:
```bash
export JALA_SHIELD_KEY="paste-generated-key-here"
```

If JALA_SHIELD_KEY is not provided, the script will attempt to read a key file at `~/.jala_shield.key` or generate and persist one (development convenience). For production, prefer using a secrets manager or setting the environment variable.

## Run locally
```bash
python jalaviveka.py
```

To point to a remote AMRUT JSON endpoint:
```bash
export REMOTE_AMRUT_URL="https://example.com/amrut"
python jalaviveka.py
```

## Tests (pytest)
Install test requirements:
```bash
pip install -r requirements-dev.txt pytest cryptography requests
```

Run tests:
```bash
pytest -q
```

## What was added
- Improved key handling and logging
- `nikhilam_multiply` robust implementation with carry handling
- Unit tests for multiply, evaluate_viveka boundaries, encrypt/decrypt roundtrip
- README fragment for running & testing