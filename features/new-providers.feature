@manual @new-providers
Feature: Create new providers and generate their links
  Providers that do not exist are created and their links generated.
  Existing providers have their input fields updated but their links will not be changed.
  Links for all providers are returned in an output file together with confirmation that
  they were either NEW or EXISTING providers.

  Scenario:
    Given provider "Test Provider One" exists
    And provider "Test Provider Two" does not exist
    And both providers are included in the input file
    When the input file is processed
    Then "Test Provider One" is updated with the original link
    And "Test Provider Two" is created with a new link

