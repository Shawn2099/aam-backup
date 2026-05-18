"""Tests for concurrency guard, VSS scanner fix, and metrics on no-change runs."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from flow import ConcurrencyGuard


def test_concurrency_guard_acquire(tmp_path):
    """ConcurrencyGuard can be acquired."""
    lock_path = tmp_path / "backup.lock"
    guard = ConcurrencyGuard(lock_path)
    assert guard.acquire() is True
    assert lock_path.exists()
    guard.release()
    assert not lock_path.exists()


def test_concurrency_guard_prevents_duplicate(tmp_path):
    """ConcurrencyGuard prevents second acquire."""
    lock_path = tmp_path / "backup.lock"
    guard1 = ConcurrencyGuard(lock_path)
    guard2 = ConcurrencyGuard(lock_path)

    assert guard1.acquire() is True
    assert guard2.acquire() is False

    guard1.release()
    assert guard2.acquire() is True
    guard2.release()


def test_concurrency_guard_stale_lock(tmp_path):
    """ConcurrencyGuard removes stale lock from dead process."""
    lock_path = tmp_path / "backup.lock"
    # Write a PID that doesn't exist (use a very high number)
    lock_path.write_text("999999999")

    guard = ConcurrencyGuard(lock_path)
    assert guard.acquire() is True
    guard.release()


def test_concurrency_guard_release_idempotent(tmp_path):
    """ConcurrencyGuard release is safe to call multiple times."""
    lock_path = tmp_path / "backup.lock"
    guard = ConcurrencyGuard(lock_path)
    guard.acquire()
    guard.release()
    guard.release()  # Should not raise
    guard.release()  # Should not raise
