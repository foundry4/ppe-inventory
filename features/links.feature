@manual @links
Feature: Retrieve filtered set of links for Community Sites
  Searching with values for Borough, PCN and Service Type will present only those sites that match all criteria.

  Scenario Outline: Retrieve filtered list of site links
    Given the expected sites exist
    When I search for sites matching "<Borough>", "<PCN>" and "<Service Type>"
    Then I can see the Links Result page
    And I am shown links for the matching "<Sites>"
    Examples:
      | Borough            | PCN            | Service Type                 | Sites                                                  |
      | Barking & Dagenham | Test East      | Primary Care - GP Federation | Site One LS1 5TY, Site Two LS2 12PL, Site Four LS4 5TY |
      | Havering           | Test West Four | Primary Care - GP Federation | Site Nine LS9 4RT, Site Seven LS7 5TY                  |
      | Newham             | Test Central   | Primary Care - GP Federation | Site Five LS5 12PL, Site Six LS6 4RT                   |