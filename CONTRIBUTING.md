# Contributing to QQ Music Decryptor

Thank you for considering contributing! This project is licensed under **AGPL v3** — any modifications must also be open source under the same license.

## How to Contribute

### 1. Reporting Issues

- Check existing issues before opening a new one
- Include: Python version, Frida version, QQ Music version, and full error logs
- Describe steps to reproduce the bug

### 2. Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run basic verification: `pip install -e .` and test CLI commands
5. Commit with clear messages (conventional commits preferred)
6. Push and open a Pull Request

### 3. Development Setup

```bash
git clone https://github.com/your-username/qqmusic-decryptor.git
cd qqmusic-decryptor
pip install -r requirements.txt
pip install -e .  # for global CLI commands
```

### 4. Code Style

- Python: follow PEP 8
- Keep imports organized (stdlib, third-party, local)
- Add docstrings for public functions
- No trailing whitespace

### 5. AGPL v3 Compliance

By contributing, you agree that your contributions will be licensed under AGPL v3. Ensure your code doesn't include incompatible dependencies.

## Questions?

Open an issue with the "question" label.
