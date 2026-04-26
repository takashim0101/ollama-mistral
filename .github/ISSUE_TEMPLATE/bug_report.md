name: Bug Report
description: Report a bug or issue
title: "[BUG] "
labels: ["bug"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting a bug! Please fill out the form below to help us understand and fix the issue.

  - type: checkboxes
    id: prerequisites
    attributes:
      label: Prerequisites
      description: Please verify you have completed these steps
      options:
        - label: I have searched the existing issues
          required: true
        - label: I have read the README and documentation
          required: true
        - label: This is not a duplicate of an existing issue
          required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Clearly describe the bug
      placeholder: "What happened?"
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: How can we reproduce this bug?
      placeholder: |
        1. Start with...
        2. Then...
        3. Finally...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should have happened?
      placeholder: "I expected..."
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened?
      placeholder: "Instead, it..."
    validations:
      required: true

  - type: dropdown
    id: environment
    attributes:
      label: Environment
      description: Where did this occur?
      options:
        - Windows
        - macOS
        - Linux
        - Docker
        - Other
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Logs or Error Messages
      description: Paste relevant error logs or error messages
      render: bash

  - type: textarea
    id: additional
    attributes:
      label: Additional Context
      description: Anything else we should know?
      placeholder: "Screenshots, configuration details, etc."
