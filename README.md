# CAultron110

## 🧬 Quantum-Inspired Security Model

CAultron110 isn’t just a cryptographic tool — it’s a novel exploration of deterministic chaos, entropy injection, and emergent complexity inspired by living systems.

At its core lies a 1D cellular automaton (CA) governed by Rule 110, a known Turing-complete system capable of universal computation. But instead of letting the CA evolve freely, we perturb it — constantly — by reinjecting the original seed (derived from password, timestamp, and iteration count).

## 🧠 The Analogy

We draw a parallel between this system and the behavior of quantum systems under continuous observation:

| Quantum Concept         | CAultron110 Mechanism                                 |
|------------------------|------------------------------------------------------|
| Wavefunction evolution | Cellular automaton iteration                          |
| Observer interaction   | Seed re-injection every iteration                     |
| Collapse / projection  | SHA-512 hash of final CA state (for keying)           |
| Entanglement           | Seed influences every step, not just init             |
| Decoherence            | Outer universe with noise & randomized layout         |
| No-cloning theorem     | Key is irrecoverable without full input set           |

The CA evolves like a quantum system—until it “observes” itself via the persistent reintroduction of its own seed. This prevents extinction, avoids trivial attractors, and guarantees irreducible complexity.

## 🔄 Entropy-Reinforced Evolution

Each time the database is encrypted or saved:

- The system derives a deterministic inner universe size and layout from the password, timestamp, and iteration count.
- A fixed-size outer universe acts as a container, hiding size- and location-based metadata.
- The original seed is XOR-reinjected into the evolving CA state every round, ensuring persistent, chaotic interference.
- After a defined number of iterations, the entire universe is hashed with SHA-512 to derive encryption material.

## 🧩 Why This Matters

- **State never settles:** There's no steady state due to continual reintroduction of the entropy core.
- **Extremely sensitive to input:** A one-bit change in password or timestamp results in a totally different encryption state.
- **Impossible to reverse:** Without the password, timestamp, and correct iteration number, recovery is infeasible.
- **Metadata-secure:** The ciphertext size and structure reveal nothing about the password or evolution history.

> “CAultron110 is not a black box. It’s a live experiment in digital quantum chaos.”
