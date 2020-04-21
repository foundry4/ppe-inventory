Feature: Create new providers and generate their links
  Providers not already in the datatsore are added and a new link generated for them.
  Any attempt to add a provider with a key that already exists will not update the datastore.
  In all cases the result including the link is returned in an output file.

  Scenario: Add new provider
  Given that the new provider does not exist
  When I attempt to add the new provider
  Then I am informed that the new provider record was created
  And the link for the provider is returned

  Scenario: Attempt to add new provider when that provider already exists
  Given that the new provider does exist
  When I attempt to add the new provider
  Then I am informed that no new provider record was created
  And the link for the provider is returned