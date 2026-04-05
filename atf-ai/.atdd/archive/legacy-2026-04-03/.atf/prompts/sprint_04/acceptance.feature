Feature: [Sprint 04] Feedback and state tracking

  Scenario: Previously passed sprint is recorded in state file
    Given the state file exists
    Then sprint "sprint_02" should have status "passed"

  Scenario: WebUser navigates to confirm app is working
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"

  Scenario: ApiClient confirms external API works
    Given I am an ApiClient
    When I call GET "https://jsonplaceholder.typicode.com/todos/1"
    Then the response status should be 200
    And the response should contain "delectus aut autem"
