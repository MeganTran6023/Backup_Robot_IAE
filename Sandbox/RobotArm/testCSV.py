#!/usr/bin/env python3
"""
Servo Full Range Test Script
----------------------------
Moves all servo combinations through full range (-1 → +1 → 0 → -1 → 0),
total cycle duration = 1 second per test. Logs progress to CSV and can resume.
"""

import csv
import os
import time
import itertools
from datetime import datetime
from adafruit_servokit import ServoKit

# === CONFIGURATION ===
kit = ServoKit(channels=16)

AVAILABLE_CHANNELS = [12, 13, 14, 15]   # Channels to test
LOG_FILENAME = "servo_fullrange_log.csv"

# Total duration of full cycle (seconds)
TOTAL_CYCLE_DURATION = 1.0
COOLDOWN_BETWEEN_TESTS = 1  # seconds

# === LOGGING ===

def init_log():
    with open(LOG_FILENAME, "a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow([
                "timestamp", "trial_id", "channels",
                "event", "throttle", "notes"
            ])

def log_event(trial_id, channels, event, throttle, notes=""):
    with open(LOG_FILENAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            trial_id,
            ",".join(str(c) for c in channels),
            event,
            throttle,
            notes
        ])

def get_completed_trials():
    completed = set()
    if not os.path.exists(LOG_FILENAME):
        return completed
    with open(LOG_FILENAME, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["event"].strip().lower() == "stop":
                completed.add(row["trial_id"])
    return completed

# === SERVO CONTROL ===

def run_fullrange_test(channels, trial_id):
    """Move all channels -1 -> +1 -> 0 in equal time slices to fill TOTAL_CYCLE_DURATION."""
    print(f"→ {trial_id}: Channels {channels}, full range cycle ({TOTAL_CYCLE_DURATION}s)")

    # Divide total cycle into 3 phases: +1, -1, 0
    phase_duration = TOTAL_CYCLE_DURATION / 3.0

    # Start neutral
    for ch in channels:
        kit.continuous_servo[ch].throttle = 0
    log_event(trial_id, channels, event="start_neutral", throttle=0)

    # Phase 1: full clockwise (+1)
    for ch in channels:
        kit.continuous_servo[ch].throttle = 1
    log_event(trial_id, channels, event="throttle_+1", throttle=1)
    time.sleep(phase_duration)

    # Phase 2: full counter-clockwise (-1)
    for ch in channels:
        kit.continuous_servo[ch].throttle = -1
    log_event(trial_id, channels, event="throttle_-1", throttle=-1)
    time.sleep(phase_duration)

    # Phase 3: back to neutral (0)
    for ch in channels:
        kit.continuous_servo[ch].throttle = 0
    log_event(trial_id, channels, event="stop", throttle=0)
    print(f"✓ Completed {trial_id}")
    time.sleep(COOLDOWN_BETWEEN_TESTS)

# === TEST PLAN BUILDER ===

def build_test_plan():
    """Generate all 1–N servo combinations."""
    plan = []
    trial_num = 0
    for r in range(1, len(AVAILABLE_CHANNELS)+1):
        for combo in itertools.combinations(AVAILABLE_CHANNELS, r):
            trial_num += 1
            trial_id = f"trial_{trial_num:03d}"
            plan.append((trial_id, list(combo)))
    return plan

# === MAIN PROGRAM ===

def main():
    print("Servo Full Range Test (resume capable)")
    print("--------------------------------------")

    init_log()
    completed = get_completed_trials()
    plan = build_test_plan()

    total_tests = len(plan)
    done_tests = len(completed)
    print(f"Resuming: {done_tests}/{total_tests} tests already complete.\n")

    try:
        for trial_id, channels in plan:
            if trial_id in completed:
                print(f"[SKIP] {trial_id} already completed.")
                continue
            run_fullrange_test(channels, trial_id)

        print("\n✅ All tests complete. Servos off.")
        for ch in AVAILABLE_CHANNELS:
            kit.continuous_servo[ch].throttle = 0

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user. Stopping servos safely.")
        for ch in AVAILABLE_CHANNELS:
            kit.continuous_servo[ch].throttle = 0
        log_event("interrupted", AVAILABLE_CHANNELS, event="keyboard_interrupt", throttle=0,
                  notes="User stopped test early.")
        print("Progress saved. Run script again to resume remaining tests.")

if __name__ == "__main__":
    main()
