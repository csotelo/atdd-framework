Feature: [Sprint 02] Docker runner executes tests

  Scenario: WebUser can navigate inside Docker
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"

  Scenario: ApiClient can call a public API
    Given I am an ApiClient
    When I call GET "https://jsonplaceholder.typicode.com/users/1"
    Then the response status should be 200
    And the response should contain "Leanne Graham"
