# Contributing to nodus-delivery

## Setup

```bash
git clone https://github.com/Masterplanner25/nodus-delivery.git
cd nodus-delivery
pip install -e ".[dev]"
pip install "nodus-channels>=0.1.0"
```

## Running tests

```bash
pytest tests/ -q
```

## Code style

- Python 3.11+
- `ChunkStrategy` is a protocol — new chunkers satisfy it by structure,
  not inheritance
- Type hints on all public functions

## Submitting changes

1. Fork the repo and create a branch from `main`
2. Add tests for any new behaviour
3. Ensure `pytest tests/ -q` passes
4. Open a pull request with a description of what changes and why
