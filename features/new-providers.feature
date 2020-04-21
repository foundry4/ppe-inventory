@manual @new-providers
Feature: Create new providers and generate their links
  Providers not already in the datatsore are added and a new link generated for them.
  Existing providers will have their input fields updated but their link will not be changed.
  In all cases the results including the links are returned in an output file.

  Scenario: Add new provider
  Given that the new provider does not exist
  When I attempt to add the new provider
  Then I am informed that the new provider record was created
  And the link for the provider is returned

  Scenario: Attempt to add new provider when that provider already exists
  Given that the new provider does exist
  When I attempt to add the new provider
  Then I am informed that the provider existed
  And the link for the provider is returned