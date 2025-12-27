# Contributing to VoiceStudio Quantum+

Thank you for your interest in contributing to VoiceStudio Quantum+! This guide will help you get started.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Git Workflow](#git-workflow)
5. [Pull Request Process](#pull-request-process)
6. [Testing Requirements](#testing-requirements)
7. [Documentation Requirements](#documentation-requirements)
8. [Development Setup](#development-setup)
9. [Code Quality Standards](#code-quality-standards)
10. [Getting Help](#getting-help)

---

## Code of Conduct

### Our Standards

- **Be respectful:** Treat all contributors with respect
- **Be inclusive:** Welcome contributors of all backgrounds
- **Be constructive:** Provide helpful feedback
- **Be professional:** Maintain professional communication

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Any conduct that could reasonably be considered inappropriate

---

## How to Contribute

### Reporting Bugs

1. **Check existing issues:** Search GitHub Issues to see if the bug is already reported
2. **Create new issue:** If not found, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs. actual behavior
   - System information (OS, version, etc.)
   - Log files (if applicable)

### Suggesting Features

1. **Check existing issues:** Search for similar feature requests
2. **Create feature request:** Include:
   - Clear description of the feature
   - Use case and benefits
   - Proposed implementation (if applicable)
   - Examples or mockups (if applicable)

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/my-feature`
3. **Make your changes:** Follow code style guidelines
4. **Write tests:** Add tests for new functionality
5. **Update documentation:** Document your changes
6. **Commit changes:** Use descriptive commit messages
7. **Push to your fork:** `git push origin feature/my-feature`
8. **Create pull request:** Follow PR process below

---

## Code Style Guidelines

### C# Code Style

**General:**
- Use 4 spaces for indentation (not tabs)
- Use meaningful variable and method names
- Follow C# naming conventions:
  - Classes: `PascalCase`
  - Methods: `PascalCase`
  - Properties: `PascalCase`
  - Fields: `_camelCase` (private), `camelCase` (public)
  - Local variables: `camelCase`
  - Constants: `PascalCase`

**Async/Await:**
- Always use `async`/`await` for I/O operations
- Use `ConfigureAwait(false)` in library code
- Use `CancellationToken` for cancellable operations

**Error Handling:**
- Use specific exception types
- Include meaningful error messages
- Don't swallow exceptions
- Log errors appropriately

See [CODE_STYLE_GUIDE.md](docs/developer/CODE_STYLE_GUIDE.md) for detailed C# style guidelines.

### Python Code Style

**General:**
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful names
- Add type hints where possible

**Docstrings:**
- Use Google-style docstrings
- Document all public functions and classes
- Include parameter descriptions
- Include return value descriptions
- Include exceptions raised

See [CODE_STYLE_GUIDE.md](docs/developer/CODE_STYLE_GUIDE.md) for detailed Python style guidelines.

### XAML Style

**General:**
- Use consistent indentation (4 spaces)
- Use meaningful names for controls
- Use design tokens (VSQ.*) for styling
- Keep code-behind minimal

See [CODE_STYLE_GUIDE.md](docs/developer/CODE_STYLE_GUIDE.md) for detailed XAML style guidelines.

---

## Git Workflow

### Branch Naming

**Format:** `{type}/{description}`

**Types:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes
- `chore/` - Maintenance tasks

**Examples:**
- `feature/add-voice-morphing`
- `fix/audio-playback-crash`
- `docs/update-api-reference`
- `refactor/backend-client-split`

### Commit Messages

**Format:** `{type}: {description}`

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

**Examples:**
```
feat: Add voice morphing panel
fix: Resolve audio playback crash on Windows 10
docs: Update API documentation for batch endpoints
refactor: Split BackendClient into feature-specific clients
test: Add integration tests for voice synthesis
```

**Guidelines:**
- Use imperative mood ("Add feature" not "Added feature")
- Keep first line under 72 characters
- Add detailed description if needed (separated by blank line)
- Reference issues: "Fixes #123"

### Workflow Steps

1. **Update main branch:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: Add my feature"
   ```

4. **Push to fork:**
   ```bash
   git push origin feature/my-feature
   ```

5. **Create pull request** (via GitHub)

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No TODO comments or placeholders
- [ ] Code is 100% complete (see [NO_STUBS_PLACEHOLDERS_RULE.md](docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md))

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests pass
```

### Review Process

1. **Automated checks:** CI/CD runs tests and linting
2. **Code review:** At least one maintainer reviews
3. **Feedback:** Address review comments
4. **Approval:** Maintainer approves PR
5. **Merge:** PR merged to main branch

### PR Guidelines

- **Keep PRs focused:** One feature/fix per PR
- **Keep PRs small:** Easier to review
- **Update documentation:** Document all changes
- **Add tests:** Test new functionality
- **Respond to feedback:** Address review comments promptly

See [CODE_REVIEW_CHECKLIST.md](docs/developer/CODE_REVIEW_CHECKLIST.md) for detailed code review guidelines.

---

## Testing Requirements

### Frontend Tests

**Unit Tests:**
- Test ViewModels in isolation
- Mock services
- Test business logic

**Integration Tests:**
- Test API communication
- Test UI interactions
- Test end-to-end workflows

### Backend Tests

**Unit Tests:**
- Test route handlers
- Test engine functionality
- Test utility functions

**Integration Tests:**
- Test API endpoints
- Test engine integration
- Test WebSocket communication

### Running Tests

**Frontend:**
```bash
dotnet test src/VoiceStudio.App.Tests/
```

**Backend:**
```bash
pytest backend/tests/
```

### Test Coverage

- Aim for 80%+ code coverage
- Cover edge cases
- Cover error scenarios
- Cover happy paths

See [TESTING_INFRASTRUCTURE.md](docs/testing/TESTING_INFRASTRUCTURE.md) for detailed testing documentation.

---

## Documentation Requirements

### Code Documentation

**C# XML Comments:**
```csharp
/// <summary>
/// Synthesizes speech from text using a voice profile.
/// </summary>
/// <param name="profileId">Voice profile ID</param>
/// <param name="text">Text to synthesize</param>
/// <param name="cancellationToken">Cancellation token</param>
/// <returns>Voice synthesis result with audio ID and quality metrics</returns>
/// <exception cref="ArgumentException">Thrown when profileId is null or empty</exception>
public async Task<VoiceSynthesizeResponse> SynthesizeAsync(
    string profileId,
    string text,
    CancellationToken cancellationToken = default)
{
    // Implementation
}
```

**Python Docstrings:**
```python
def synthesize(text: str, profile_id: str) -> VoiceSynthesizeResponse:
    """
    Synthesize speech from text using a voice profile.
    
    Args:
        text: Text to synthesize (1-10000 characters)
        profile_id: Voice profile ID
    
    Returns:
        VoiceSynthesizeResponse with audio_id and quality_metrics
    
    Raises:
        HTTPException: If profile not found or synthesis fails
    """
    # Implementation
```

### API Documentation

- Document all endpoints
- Include request/response examples
- Document error responses
- Update when endpoints change

### User Documentation

- Update user guides for new features
- Add tutorials for new workflows
- Update troubleshooting guide for new issues

---

## Development Setup

See [SETUP.md](docs/developer/SETUP.md) and [QUICK_START.md](docs/developer/QUICK_START.md) for complete development environment setup instructions.

**Quick Start:**
1. Clone repository
2. Install prerequisites (.NET 8, Python 3.10+)
3. Install dependencies
4. Run backend: `python -m uvicorn backend.api.main:app`
5. Run frontend: Open in Visual Studio and run

---

## Code Quality Standards

### 100% Complete Rule

**CRITICAL:** All code must be 100% complete. No stubs or placeholders.

**Forbidden:**
- `// TODO: Implement this`
- `throw new NotImplementedException()`
- `[PLACEHOLDER]`
- Empty methods with only comments

**Required:**
- Full implementation
- Error handling
- Tests
- Documentation

See [NO_STUBS_PLACEHOLDERS_RULE.md](docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md) for details.

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] No TODO comments or placeholders
- [ ] Error handling implemented
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No code duplication
- [ ] Performance considered
- [ ] Security considered

See [CODE_REVIEW_CHECKLIST.md](docs/developer/CODE_REVIEW_CHECKLIST.md) for comprehensive code review guidelines.

---

## Getting Help

### Resources

- **Documentation:** `docs/` directory
- **Architecture:** [ARCHITECTURE.md](docs/developer/ARCHITECTURE.md)
- **API Reference:** [API_REFERENCE.md](docs/api/API_REFERENCE.md)
- **Quick Start:** [QUICK_START.md](docs/developer/QUICK_START.md)
- **Code Style:** [CODE_STYLE_GUIDE.md](docs/developer/CODE_STYLE_GUIDE.md)

### Communication

- **GitHub Issues:** For bugs and feature requests
- **Discussions:** For questions and discussions (if available)
- **Pull Requests:** For code contributions

---

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

---

**Thank you for contributing to VoiceStudio Quantum+!**

For more detailed information, see the complete [Contributing Guide](docs/developer/CONTRIBUTING.md).

