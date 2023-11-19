#!/usr/bin/env python3

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List
from termcolor import colored


@dataclass
class TestSetup:
    """Test Setup, build, run and stop the backend"""

    name: str
    short: str
    host: str
    dir: str
    build: List[str]
    run: List[str]


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
    proc.send_signal(signal.SIGTERM)
    time.sleep(1)  # wait for server to stop
    if proc.poll() is None:
        print("terminating process failed, killing process")
        proc.kill()


def run_integration_tests(label: str, host: str):
    """Run integration tests

    Args:
        host (str): backend host

    Returns:
        TestResult: test result
    """
    cmd = [
        "pnpm",
        "exec",
        "cucumber-js",
        "--format",
        "summary",
        "--format",
        f"junit:test_results/{label}.xml",
    ]
    env = dict(os.environ)
    env.update({"API_URL": host})

    subprocess.run(cmd, cwd="./tests", env=env, check=False)


setups = [
    TestSetup(
        "C# (ASP.NET)",
        "asp.net",
        "127.0.0.1:5000",
        "backend/asp.net",
        ["dotnet", "build", "EShop/EShop.csproj", "-c", "Release"],
        ["EShop/bin/Release/net7.0/EShop"],
    ),
    TestSetup(
        "Go (Gin)",
        "gin",
        "127.0.0.1:8080",
        "backend/gin",
        ["go", "build", "."],
        ["./eshop"],
    ),
    TestSetup(
        "Rust (Axum)",
        "axum",
        "127.0.0.1:3000",
        "backend/axum",
        ["cargo", "build", "--release"],
        ["./target/release/eshop"],
    ),
    TestSetup(
        "Node.js (Express)",
        "express",
        "127.0.0.1:3000",
        "backend/express",
        ["pnpm", "run", "build"],
        ["node", "dist/index.js"],
    ),
    TestSetup(
        "Java (Spring Boot)",
        "spring",
        "127.0.0.1:8080",
        "backend/spring",
        ["./gradlew", "build"],
        ["./gradlew", "bootRun"],
    ),
    TestSetup(
        "Python (Django)",
        "django",
        "127.0.0.1:8000",
        "backend/django",
        [],
        ["python", "manage.py", "runserver"],
    ),
]


def main():
    """Main function"""
    env = dict(os.environ)

    for setup in setups:
        print("")
        if setup.build:
            print(colored(f"Building {setup.name}", attrs=["dark"]))
            subprocess.run(
                setup.build, cwd=setup.dir, env=env, check=True, capture_output=True
            )
        print(f"Running tests for {colored(setup.name, 'blue')}")
        proc = start_server(setup.run, setup.dir, env)
        run_integration_tests(setup.short, setup.host)
        stop_server(proc)


if __name__ == "__main__":
    main()
