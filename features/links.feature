@manual @links
Feature: Retrieve filtered set of links for Community Sites
  Searching with values for Borough, PCN and Service Type will present only those sites that match all criteria.

  Scenario Outline: Retrieve filtered list of site links
    Given the expected community sites exist
    When I search for sites matching "<Borough>", "<PCN>" and "<Service Type>"
    Then I can see the Links Result page
    And I am shown links for the matching "<Sites>"
    Examples:
      | Borough            | PCN       | Service Type                 | Sites                                             |
      | Barking & Dagenham | East      | Primary Care - GP Federation | Links Site Four LS4 5TY                           |
      | Havering           | West Four | Primary Care - GP Federation | Links Site Nine LS9 4RT, Links Site Seven LS7 5TY |
      | Barking & Dagenham | South Six | Primary Care - GP Federation | Links Site Five LS5 12PL, Links Site Six LS6 4RT  |
