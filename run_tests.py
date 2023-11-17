#!/usr/bin/env python3
import json
import os
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List
from termcolor import colored

@dataclass
class TestSetup:
    """Test Setup, build, run and stop the backend"""

    name: str
    host: str
    dir: str
    build: List[str]
    run: List[str]


@dataclass
class TestResult:
    """Test Result, hold the overall result and individual pass/fail numbers"""

    passed: bool
    num_passed: int
    num_skipped: int
    num_failed: int


def start_server(cmd: List[str], pwd: str, env: Dict) -> subprocess.Popen:
    """Start backend

    Args:
        cmd (List[str]): _description_
        pwd (str): _description_

    Returns:
        subprocess.Popen: _description_
    """
    proc = subprocess.Popen(
        cmd, env=env, cwd=pwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(2)  # wait for server to start
    return proc


def stop_server(proc: subprocess.Popen):
    """Stop the server process

    Args:
        proc (subprocess.Popen): Process to terminate
    """
    proc.terminate()
    if proc.poll() is None:
        proc.kill()


def run_integration_tests(host: str) -> TestResult:
    """Run integration tests

    Args:
        host (str): backend host

    Returns:
        TestResult: test result
    """
    cmd = ["pnpm", "exec", "cucumber-js", "--format", "message"]
    env = dict(os.environ)
    env.update({"API_URL": host})

    result = subprocess.run(
        cmd,
        cwd="./tests",
        env=env,
        check=False,
        capture_output=True,
    )

    messages = [json.loads(s) for s in result.stdout.decode("utf-8").splitlines()]
    test_finished_messages = [m for m in messages if "testStepFinished" in m]

    passed = 0
    skipped = 0
    failed = 0
    for msg in test_finished_messages:
        if msg["testStepFinished"]["testStepResult"]["status"] == "PASSED":
            passed += 1
        elif msg["testStepFinished"]["testStepResult"]["status"] == "SKIPPED":
            skipped += 1
        elif msg["testStepFinished"]["testStepResult"]["status"] == "FAILED":
            failed += 1

    return TestResult(result.returncode == 0, passed, skipped, failed)


setups = [
    TestSetup(
        "C# (ASP.NET)",
        "127.0.0.1:5000",
        "backend/asp.net",
        ["dotnet", "build", "EShop/EShop.csproj", "-c", "Release"],
        ["EShop/bin/Release/net7.0/EShop"],
    ),
    TestSetup(
        "Go (Gin)",
        "127.0.0.1:8080",
        "backend/gin",
        ["go", "build", "."],
        ["./eshop"],
    ),
    TestSetup(
        "Rust (Axum)",
        "127.0.0.1:3000",
        "backend/axum",
        ["cargo", "build", "--release"],
        ["./target/release/eshop"],
    ),
    TestSetup(
        "Node.js (Express)",
        "127.0.0.1:3000",
        "backend/express",
        ["pnpm", "run", "build"],
        ["pnpm", "run","start"],
    ),
    TestSetup(
        "Java (Spring Boot)",
        "127.0.0.1:8080",
        "backend/spring",
        ["./gradlew", "build"],
        ["./gradlew", "bootRun"],
    )
]


def main():
    """Main function"""
    env = dict(os.environ)
    env.update({"SQLITE_DATABASE_FILE": "tests/db/db.sqlite"})

    for setup in setups:
        print("")
        print(f"Building {setup.name}")
        subprocess.run(
            setup.build, cwd=setup.dir, env=env, check=True, capture_output=True
        )
        print(f"Running tests for {colored(setup.name, 'blue')}")
        proc = start_server(setup.run, setup.dir, env)
        result = run_integration_tests(setup.host)
        stop_server(proc)

        if result.passed:
            print(colored("All steps passed", "green"))
        else:
            print(colored("Some steps failed", "red"))
        print(
            f"Passed: {result.num_passed}, Skipped: {result.num_skipped}, Failed: {result.num_failed}"
        )


if __name__ == "__main__":
    main()
