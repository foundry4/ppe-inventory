Feature: Redirect from Registration page
  The user should be redirected to the Form page from the Registration page.

  Scenario: Successful Registration
    When I visit the registration page with a valid link
    Then I can see the Form page
    And I see the provider name

  Scenario: Unsuccessful Registration
    When I visit the registration page with an invalid link
    Then I can see the Form page
    And I see that I am denied access