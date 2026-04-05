Feature: [Sprint 01] ATF CLI scaffolding

  Scenario: State file is initialized by the framework
    Given the state file exists

  Scenario: Public web target is reachable inside Docker
    Given I am a WebUser
    When I navigate to "https://the-internet.herokuapp.com"
    Then I should see "Welcome to the-internet"
