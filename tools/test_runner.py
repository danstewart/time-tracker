#!/usr/bin/env python

# Inspired by https://allanderek.github.io/posts/flask-%2B-coverage-analysis/
# - Start the dev server under coverage.py
# - Do any setup required
# - Run tests
# - Generate coverage report

import contextlib
import os
import signal
import subprocess
import sys

env = os.environ.copy()
env["TEST_MODE"] = "yes"


def main():
    with start_server():
        setup()
        run_tests()

    generate_coverage()


@contextlib.contextmanager
def start_server():
    server_command = ["coverage", "run", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

    print("Starting test server...")
    sys.stdout.flush()

    server = subprocess.Popen(server_command, stderr=subprocess.PIPE, env=env)
    for line in server.stderr:  # type: ignore
        if line.startswith(b" * Running on"):
            break

    yield

    server.send_signal(signal.SIGINT)
    server.wait(timeout=30)


def setup():
    # Run migrations
    print("Running migrations...")
    sys.stdout.flush()

    migrate_command = ["flask", "db", "upgrade"]
    migrate = subprocess.Popen(migrate_command, env=env)
    migrate.wait(timeout=30)

    # Seed test data
    print("Seeding test database...")
    sys.stdout.flush()

    seed_command = ["flask", "data", "seed-test-db"]
    seed = subprocess.Popen(seed_command, env=env)
    seed.wait(timeout=30)


def run_tests():
    print("Running tests...")
    sys.stdout.flush()

    test_command = ["pytest"]
    test_process = subprocess.Popen(test_command, env=env)
    test_process.wait(timeout=120)


def generate_coverage():
    os.system("coverage report -m")


if __name__ == "__main__":
    main()
