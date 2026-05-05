# Contributing to RAG-SQL-Python-Assistant

First off, thank you for considering contributing to this project! It's people like you that make the open-source community such an amazing place to learn, inspire, and create.

---

## 🛠️ Development Setup

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/RAG-SQL-Python-Assistant.git
   ```
3. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Set up the frontend**:
   ```bash
   cd frontend
   npm install
   ```

---

## 🌿 Branching Strategy

We follow a simple branching model:
- `main`: Production-ready code.
- `develop`: Ongoing development.
- `feature/name`: New features.
- `fix/name`: Bug fixes.
- `docs/name`: Documentation updates.

---

## 📝 Commit Message Guidelines

We enforce [Conventional Commits](https://www.conventionalcommits.org/). This allows us to automate changelog generation and versioning.

**Format:** `<type>(<scope>): <description>`

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries

**Example:**
`feat(pipeline): add support for async query expansion`

---

## ✅ Pull Request Process

1. Create a new branch for your feature or fix.
2. Ensure your code follows the existing style (use `black` for Python and `prettier` for JS).
3. Update the documentation if you are adding/changing features.
4. Open a PR against the `develop` branch.
5. Provide a clear description of the changes and link any related issues.

---

## 🏗️ Code Quality Rules

- **Python**: Follow PEP 8. Use type hints where possible.
- **React**: Use functional components and hooks. Maintain component modularity.
- **API**: Follow RESTful principles. Ensure all new endpoints are documented in the OpenAPI spec.
- **Tests**: Add unit tests for new logic in the `backend/evals` directory.

---

## 🚀 Reporting Issues

- Use the GitHub Issue Tracker.
- Provide a clear, descriptive title.
- Include steps to reproduce the bug.
- Mention your environment (OS, Python version, Ollama version).

---

## 💎 Acknowledgments

By contributing, you agree that your contributions will be licensed under its MIT License.
