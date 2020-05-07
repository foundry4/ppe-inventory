@manual @children
Feature: Retrieve child sites for a parent
  Searching with a value for parent will present only those sites that have that parent.

  Scenario Outline: Retrieve list of child site links
    Given the expected sites exist
    When I search for child sites matching "<Parent>"
    Then I can see the Children Result page
    And I am shown links for the matching "<Sites>"
    Examples:
      | Parent         | Sites                                                                                          |
      | Test Group One | Site One LS1 5TY, Site Two LS2 12PL, Site Three LS3 4RT, Site Four LS4 5TY, Site Five LS5 12PL |
      | Test Group Two | Site Six LS6 4RT, Site Seven LS7 5TY, Site Nine LS9 4RT, Site Ten LS10 4RT                     |
