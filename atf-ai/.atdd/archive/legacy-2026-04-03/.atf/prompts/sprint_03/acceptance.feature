Feature: [Sprint 03] Screenplay actors and step definitions

  Scenario: WebUser fills and submits a form
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com/login"
    And I fill in "username" with "tomsmith"
    And I fill in "password" with "SuperSecretPassword!"
    And I click the "Login" button
    Then I should see "You logged into a secure area!"

  Scenario: WebUser sees elements on a page
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com/checkboxes"
    Then the element "input[type='checkbox']" should be visible

  Scenario: ApiClient reads a specific field
    Given I am an ApiClient
    When I call GET "https://jsonplaceholder.typicode.com/posts/1"
    Then the response status should be 200
    And the response field "userId" should equal "1"
