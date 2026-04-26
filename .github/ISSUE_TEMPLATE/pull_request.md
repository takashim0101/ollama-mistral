name: Pull Request
description: Submit a pull request
title: ""
labels: []
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thank you for contributing! Please fill out the information below.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: What changes does this PR introduce?
      placeholder: "This PR..."
    validations:
      required: true

  - type: textarea
    id: related_issues
    attributes:
      label: Related Issues
      description: "Link to related issues (e.g., fixes #123)"
      placeholder: "Closes #"

  - type: dropdown
    id: type
    attributes:
      label: Type of Change
      description: What type of change is this?
      options:
        - Feature (new functionality)
        - Bug Fix
        - Documentation
        - Performance Improvement
        - Refactoring
        - Test
        - CI/CD
        - Other
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Testing
      description: Have you tested these changes?
      options:
        - label: I have run local tests
          required: true
        - label: All tests pass
          required: true
        - label: I have added new tests (if applicable)

  - type: checkboxes
    id: documentation
    attributes:
      label: Documentation
      description: Is documentation updated?
      options:
        - label: I have updated the README or documentation
        - label: Code comments are clear and helpful

  - type: checkboxes
    id: standards
    attributes:
      label: Code Standards
      description: Does this follow project standards?
      options:
        - label: Code follows the project style guide
          required: true
        - label: No hardcoded secrets or sensitive data
          required: true
        - label: Commit messages are clear and descriptive
          required: true

  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots (if applicable)
      description: Add screenshots for UI changes
      placeholder: "Paste screenshots here"
