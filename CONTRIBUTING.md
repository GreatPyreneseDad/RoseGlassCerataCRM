# Contributing to Rose Glass Cerata CRM

Thank you for your interest in contributing to Rose Glass Cerata CRM! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows a code of conduct based on mutual respect and constructive collaboration. Please be respectful and professional in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title**: Describe the issue concisely
2. **Steps to reproduce**: Detailed steps to recreate the bug
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, dependencies
6. **Code sample**: Minimal code to reproduce (if applicable)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

1. **Use case**: Why is this enhancement needed?
2. **Proposed solution**: How would you implement it?
3. **Alternatives**: Other approaches you considered
4. **CERATA alignment**: How does this fit with the biological evolution philosophy?

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Follow the existing code style
   - Add docstrings to new functions/classes
   - Update documentation if needed
   - Add tests for new functionality
4. **Test your changes**: Run `python3 demo.py` to validate
5. **Commit your changes**: Use clear, descriptive commit messages
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a pull request**

### Commit Message Guidelines

Follow this format:

```
Brief summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain the problem this commit solves and why you chose
this approach.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues: "Fixes #123" or "Related to #456"
```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/RoseGlassCerataCRM.git
cd RoseGlassCerataCRM

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-asyncio mypy ruff

# Run demo to validate
python3 demo.py
```

## Code Style

- **Python**: Follow PEP 8
- **Type hints**: Use type hints where appropriate
- **Docstrings**: Google-style docstrings for all public functions/classes
- **Line length**: 100 characters (enforced by ruff)

### Example Docstring

```python
def perceive(self, lead: LeadData) -> LeadCoherence:
    """
    Perceive a lead through the Rose Glass lens.

    Args:
        lead: Raw lead data to analyze

    Returns:
        LeadCoherence object with dimensional analysis

    Raises:
        ValueError: If lead data is invalid

    Example:
        >>> lens = RoseGlassCRMLens()
        >>> coherence = lens.perceive(lead)
        >>> print(coherence.qualification_tier)
        'hot'
    """
```

## Testing

We use pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_rose_glass_lens.py -v
```

When adding new features, please include tests.

## CERATA Philosophy Alignment

Contributions should align with CERATA principles:

1. **Perception, Not Prescription**: Let the system perceive patterns, don't hardcode rules
2. **Evolution, Not Configuration**: Use trials for changes, not manual parameter tweaking
3. **Learning, Not Deleting**: Extract value from failures, don't discard them
4. **Biology, Not Algorithms**: Prefer biological metaphors and optimization

### Anti-Patterns to Avoid

❌ **Don't**:
- Add arbitrary scoring thresholds without biological justification
- Create manual override switches that bypass Rose Glass
- Delete failed leads instead of burying them in graveyard
- Implement features that can't evolve through trials

✅ **Do**:
- Use biological optimization (Michaelis-Menten, coupling, etc.)
- Add nutrients to graveyard learning
- Create trial-able variations
- Maintain transparency in perception

## Areas for Contribution

We welcome contributions in these areas:

### High Priority

1. **CRM Integrations**: Salesforce, HubSpot, Pipedrive connectors
2. **Test Coverage**: Expand pytest test suite
3. **Documentation**: Improve docstrings, add tutorials
4. **Web Dashboard**: React/Vue dashboard for trial monitoring

### Medium Priority

5. **ML Enhancements**: Deal value prediction, churn risk
6. **Semantic Analysis**: NLP for pain point extraction
7. **API Endpoints**: REST API for qualification service
8. **Performance**: Async optimization, caching

### Research/Experimental

9. **Alternative Lenses**: Industry-specific calibrations
10. **Graveyard Intelligence**: Pattern detection improvements
11. **Trial Strategies**: Advanced A/B testing approaches
12. **Hunter Algorithms**: Smarter web discovery

## Questions?

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers at [your-email]

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special mention for CERATA philosophy alignment

Thank you for helping evolve Rose Glass Cerata CRM! 🌹
