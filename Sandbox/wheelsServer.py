# motor_pin_permutations_high_low.py

import lgpio
import time
import itertools
import json
import os

# GPIO setup
h = lgpio.gpiochip_open(0)

# Original pins
pins = [16, 21, 19, 13, 20, 26]
roles = ["IN1", "IN2", "ENA", "IN3", "IN4", "ENB"]

# Claim pins as outputs
for pin in pins:
    lgpio.gpio_claim_output(h, pin)

# JSON file to save progress
PROGRESS_FILE = "tested_permutations_high_low.json"

# Load progress
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return []

# Save progress
def save_progress(tested):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(tested, f)

# Apply HIGH/LOW state to pins in a permutation
def apply_state(perm, state):
    pin_mapping = dict(zip(roles, perm))
    for i, pin in enumerate(perm):
        lgpio.gpio_write(h, pin, state[i])
    print(f"Permutation: {pin_mapping}, State: {state}")
    time.sleep(0.2)
    # Reset pins to LOW
    for pin in perm:
        lgpio.gpio_write(h, pin, 0)

# Generate all permutations and states
all_perms = list(itertools.permutations(pins))
all_states = list(itertools.product([0,1], repeat=6))

# Load tested combinations
tested = load_progress()

try:
    for perm in all_perms:
        for state in all_states:
            entry = {"perm": list(perm), "state": list(state)}
            if entry not in tested:
                apply_state(perm, state)
                tested.append(entry)
                save_progress(tested)

finally:
    # Reset all pins
    for pin in pins:
        lgpio.gpio_write(h, pin, 0)
    lgpio.gpiochip_close(h)
    print("All tests completed, pins reset.")
