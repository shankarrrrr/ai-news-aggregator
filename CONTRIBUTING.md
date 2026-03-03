# Contributing to AI-Powered Competitive Exam Intelligence System

Thank you for your interest in contributing to this project! This document provides guidelines for contributing to the codebase.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git
- Google Gemini API key

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/competitive-exam-intelligence-system.git
   cd competitive-exam-intelligence-system
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize Database**
   ```bash
   python scripts/run_migration.py
   ```

## 🧪 Development Workflow

### Code Standards

#### Python Style Guide
- Follow **PEP 8** style guidelines
- Use **Black** for code formatting: `black app/ tests/`
- Use **isort** for import sorting: `isort app/ tests/`
- Maximum line length: 127 characters

#### Type Hints
- **Required** for all function parameters and return values
- Use `typing` module for complex types
- Example:
  ```python
  from typing import List, Optional, Dict
  
  def process_articles(articles: List[Article]) -> Dict[str, int]:
      """Process articles and return statistics."""
      pass
  ```

#### Documentation
- **Google-style docstrings** required for all classes and public methods
- Include parameter types, return types, and examples
- Example:
  ```python
  def calculate_score(self, content: str, metadata: ArticleMetadata) -> RankingResult:
      """
      Calculate relevance score for an article.
      
      Args:
          content: Article content text
          metadata: Article metadata for scoring
          
      Returns:
          RankingResult with score and reasoning
          
      Raises:
          ValueError: If content is empty or metadata is invalid
          
      Example:
          >>> strategy = UPSCRankingStrategy()
          >>> result = strategy.calculate_score("RBI policy", metadata)
          >>> print(result.score)
          7.5
      """
  ```

### Testing Requirements

#### Test Coverage
- Minimum **80% code coverage** required
- Write tests for all new features
- Include both positive and negative test cases

#### Test Types
1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Property Tests**: Use Hypothesis for property-based testing

#### Running Tests
```bash
# All tests
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_scrapers.py -v

# Property tests
pytest tests/property/ -v
```

### Code Quality Checks

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

#### Linting and Type Checking
```bash
# Linting
flake8 app/ tests/

# Type checking
mypy app/ --ignore-missing-imports

# Security scan
pip-audit
```

## 🏗️ Architecture Guidelines

### Design Patterns
When adding new components, follow existing design patterns:

1. **Factory Pattern**: For creating objects dynamically
2. **Strategy Pattern**: For interchangeable algorithms
3. **Repository Pattern**: For data access abstraction
4. **Service Layer Pattern**: For business logic orchestration
5. **Template Method Pattern**: For common algorithm structures

### SOLID Principles
Ensure all code follows SOLID principles:

1. **Single Responsibility**: One reason to change per class
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subclasses must be substitutable
4. **Interface Segregation**: Focused, specific interfaces
5. **Dependency Inversion**: Depend on abstractions

### Adding New Components

#### New Scraper
```python
class NewScraper(AbstractScraper):
    """Scraper for new content source."""
    
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """Implement scraping logic."""
        pass

# Register in factory
ScraperFactory.register_scraper(SourceType.NEW_SOURCE, NewScraper)
```

#### New Ranking Strategy
```python
class NewExamRankingStrategy(AbstractRankingStrategy):
    """Ranking strategy for new exam type."""
    
    def calculate_score(self, content: str, metadata: ArticleMetadata) -> RankingResult:
        """Implement exam-specific scoring."""
        pass
```

## 📝 Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples
```bash
feat(scrapers): add new government portal scraper

- Implement scraper for ministry websites
- Add support for PDF content extraction
- Include comprehensive error handling

Closes #123
```

```bash
fix(ranking): correct UPSC strategy weight calculation

The category relevance calculation was using incorrect weights
for secondary categories, causing inflated scores.

Fixes #456
```

### Branch Naming
- **Feature branches**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-bug`
- **Documentation**: `docs/description-of-changes`
- **Refactoring**: `refactor/description-of-changes`

## 🔄 Pull Request Process

### Before Submitting
1. **Run all tests**: `pytest -v`
2. **Check code quality**: `flake8 app/ && mypy app/`
3. **Update documentation** if needed
4. **Add tests** for new functionality
5. **Update CHANGELOG.md** if applicable

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process
1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Testing** in development environment
4. **Documentation review** if applicable

## 🐛 Bug Reports

### Bug Report Template
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- Database: [e.g., PostgreSQL 13.4]

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

## 📚 Documentation

### Types of Documentation
1. **Code Documentation**: Docstrings and comments
2. **API Documentation**: Function and class interfaces
3. **User Documentation**: README and usage guides
4. **Architecture Documentation**: Design decisions and patterns

### Documentation Standards
- Use **Markdown** for all documentation
- Include **code examples** where appropriate
- Keep documentation **up-to-date** with code changes
- Use **Mermaid diagrams** for visual representations

## 🏷️ Release Process

### Versioning
We use **Semantic Versioning** (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Create GitHub release with notes
6. Deploy to production (if applicable)

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Getting Help
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check existing docs first
- **Code Review**: Learn from feedback

## 📞 Contact

For questions about contributing:
- Create a GitHub issue
- Start a discussion
- Review existing documentation

Thank you for contributing to the AI-Powered Competitive Exam Intelligence System! 🎓