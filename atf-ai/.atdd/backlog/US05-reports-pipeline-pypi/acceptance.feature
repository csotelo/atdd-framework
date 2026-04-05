Feature: [Sprint 05] Reports and full pipeline

  Scenario: WebUser can interact with a table
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com/tables"
    Then I should see "Data Tables"
    Then the element "table" should be visible

  Scenario: Report file is generated after run
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"
    And a report file should exist at "reports/sprint_05/index.html"

  Scenario: ApiClient posts data
    Given I am an ApiClient
    When I call POST "https://jsonplaceholder.typicode.com/posts" with body:
      """
      {"title": "atf test", "body": "automated", "userId": 1}
      """
    Then the response status should be 201
    And the response should contain "atf test"
