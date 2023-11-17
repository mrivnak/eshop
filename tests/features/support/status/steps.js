import assert from 'assert';
import { Given, When, Then } from '@cucumber/cucumber';
import { env } from 'process';
import fetch from 'node-fetch';


let API_URL = env.API_URL || null;

Given("I have an API URL", function () {
    assert.notStrictEqual(API_URL, null);
});

When("I send a GET request to \\/status", async function () {
    this.status = 523 // Default status code (Origin is unreachable)
    const response = await fetch('http://' + API_URL + '/status');
    this.status = response.status;
});

Then("I receive a {int} status code", function (statusCode) {
    assert.strictEqual(this.status, statusCode);
});
