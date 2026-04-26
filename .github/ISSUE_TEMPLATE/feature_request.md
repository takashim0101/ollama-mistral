name: Feature Request
description: Suggest a new feature or improvement
title: "[FEATURE] "
labels: ["enhancement"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting a feature! Please describe your idea below.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: What feature or improvement would you like to see?
      placeholder: "I would like to..."
    validations:
      required: true

  - type: textarea
    id: use_case
    attributes:
      label: Use Case
      description: Why do you need this feature? What problem does it solve?
      placeholder: "This would solve..."
    validations:
      required: true

  - type: textarea
    id: proposed_solution
    attributes:
      label: Proposed Solution
      description: How should this feature be implemented?
      placeholder: "It could work by..."

  - type: textarea
    id: alternatives
    attributes:
      label: Alternative Solutions
      description: Are there alternative approaches?
      placeholder: "Other options could include..."

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: I have searched existing feature requests
        - label: This feature aligns with the project scope
        - label: I am willing to contribute to implement this
