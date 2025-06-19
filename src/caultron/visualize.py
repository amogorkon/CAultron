import hashlib
import math

import matplotlib.pyplot as plt
import numpy as np

from .ca import derive_key, evolve, inject_seed, prepare_secrets


def run_ca(seed, steps=100, size=1024):
    """
    Run the CAultron cellular automaton with a given seed for a specified number of steps.
    The seed must be 32 bytes (256 bits).
    Returns a 2D numpy array of states, where each row is a state at a time step.
    """
    state = np.zeros(size, dtype=bool)
    states = []
    for x in range(steps):
        state = inject_seed(state, seed, nonce=f"bits={x:<12}".encode()[:12])
        state = evolve(state, seed)
        states.append(state.copy())
    return np.array(states)


def visualize_ca(states):
    plt.figure(figsize=(10, 6))
    plt.imshow(states, cmap="binary", interpolation="nearest", aspect="auto")
    plt.xlabel("Cell")
    plt.ylabel("Evolution Step")
    plt.title("CAultron CA Evolution")
    plt.show()


def print_rule_for_seed(seed):
    """
    Print the rule for a given seed.
    The seed must be 32 bytes (256 bits).
    """
    assert isinstance(seed, bytes) and len(seed) == 32, "Seed must be 32 bytes."
    meta_rule = seed[:4]
    rule_bits = int.from_bytes(meta_rule, "big")
    core_rule = (rule_bits >> 20) & 0xFF  # bits 20-27
    neighborhood_size = ((rule_bits >> 18) & 0x3) + 3  # bits 18-19, values 0-3 → 3-6
    boundary = (rule_bits >> 17) & 0x1  # bit 17
    inversion = (rule_bits >> 16) & 0x1  # bit 16
    modulation = (rule_bits >> 8) & 0xFF  # bits 8-15
    temporal = rule_bits & 0xFF  # bits 0-7

    print(f"Core Rule: {core_rule:08b}")
    print(f"Neighborhood Size: {neighborhood_size}")
    print(f"Boundary: {boundary}")
    print(f"Inversion: {inversion}")
    print(f"Modulation: {modulation:08b}")
    print(f"Temporal: {temporal:08b}")
    print("====================")


def calculate_entropy_per_state(states):
    """
    Calculate the Shannon entropy (in bits) for each CA state (row of states array).
    Returns a 1D numpy array of entropy values, one per state.
    """
    entropies = []
    for row in states:
        p1 = np.mean(row)
        p0 = 1 - p1
        # Avoid log(0) by only including nonzero probabilities
        entropy = 0.0
        if p0 > 0:
            entropy -= p0 * math.log2(p0)
        if p1 > 0:
            entropy -= p1 * math.log2(p1)
        entropies.append(entropy * len(row))  # Total bits of entropy in the row
    return np.array(entropies)


def visualize_entropy_over_time(states):
    """
    Plot the entropy per state (row) over the evolution steps.
    """
    entropies = calculate_entropy_per_state(states)
    plt.figure(figsize=(10, 4))
    plt.plot(entropies, label="Entropy per state (bits)")
    plt.xlabel("Evolution Step")
    plt.ylabel("Entropy (bits)")
    plt.title("CAultron CA State Entropy Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def hamming_distance(a: bytes, b: bytes) -> int:
    """Compute the Hamming distance between two byte strings."""
    assert len(a) == len(b)
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


def visualize_hamming_vs_counter(
    password, salt, min_counter=1, max_counter=10, size=1024
):
    """
    Visualize the Hamming distance between keys derived with increasing counter values.
    """
    secrets = prepare_secrets(*password)
    if isinstance(salt, str):
        try:
            salt_bytes = bytes.fromhex(salt)
        except ValueError:
            salt_bytes = salt.encode()
    else:
        salt_bytes = salt

    distances = []
    for counter in range(min_counter, max_counter + 1):
        concat = b"".join(secrets) + salt_bytes + counter.to_bytes(4, "big")
        base_key = hashlib.sha512(concat).digest()
        key = derive_key(secrets, salt_bytes, counter, size=size)
        distances.append(hamming_distance(base_key, key))

    from statistics import mean, median, stdev

    for f in (min, mean, median, stdev, sum):
        print(f.__name__, f"{f(distances)}")

    plt.figure(figsize=(10, 4))
    plt.plot(range(min_counter, max_counter + 1), distances, marker="o")
    plt.xlabel("Counter")
    plt.ylabel("Hamming Distance vs Counter 1")
    plt.title("Hamming Distance of Derived Keys vs Counter")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
