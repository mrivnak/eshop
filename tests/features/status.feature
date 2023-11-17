Feature: Status Check
    Scenario: Check the status of the API
        Given I have an API URL
        When I send a GET request to /status
        Then I receive a 200 status code