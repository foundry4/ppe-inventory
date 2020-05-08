@pipeline
Feature: Redirect from registration page
  The user should be redirected to the Form page from the Registration page.

  Scenario: Successful Registration
    Given I have a valid registration link
    When I visit the link
    Then I can see the form page
    And I see the provider's stock form

  Scenario: Unsuccessful Registration
    Given I have an invalid registration link
    When I visit the link
    Then I can see the home page
    And I see that I am denied access