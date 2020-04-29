@manual @new-providers
Feature: Create new providers and generate their links
  Providers that do not exist are created and their links generated.
  Existing providers have their input fields updated but their links will not be changed.
  Links for all providers are returned in an output file together with confirmation that
  they were either CREATED or UPDATED.

  Scenario:
    Given site "Test Provider One LL3 5TY" exists
    And site "Test Provider Two BR9 8YP" does not exist
    And both sites are included in the input file
    When the input file is processed
    Then site "Test Provider One LL3 5TY" is updated with the original link
    And site "Test Provider One LL3 5TY" appears in the output file as "UPDATED"
    And site "Test Provider Two BR9 8YP" is created with a new link
    And site "Test Provider Two BR9 8YP" appears in the output file as "CREATED"
