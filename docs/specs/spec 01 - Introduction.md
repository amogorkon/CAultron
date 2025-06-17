

# 1. Introduction

## Key Features

| Feature                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| **Core Algorithm**       | 1D Elementary Cellular Automaton (rule: first 8 bits of seed, 0–255)        |
| **Rule Selection**       | First 8 bits of seed select CA rule                                         |
| **Evolutions per Step**  | (Last 5 bits of seed, min=1) × universe size                                |
| **Seed Derivation**      | XOR of SHA-256 hashes of secrets (passwords, cryptographically secure random bitstring, step, etc.)         |
| **Universe Init**        | ChaCha20 CSPRNG, seed-derived key/nonce, high-entropy start                 |
| **Entropy Injection**    | ChaCha20 output injected at each key-derivation step                        |
| **Key Derivation**       | SHA-512 hash of final CA state                                              |
| **State Sensitivity**    | One-bit change in any secret yields new state/key                           |
| **Forward/Backward Secrecy** | Compromise of state does not reveal previous/next states             |
| **Key Independence**     | Keys are uncorrelated between steps                                         |
| **Quantum Resistance**   | No known quantum speedup; CA is computationally irreducible                 |
| **Metadata Security**    | Universe size/location hidden; ciphertext leaks nothing                     |
| **Extensibility**        | Modular CA/seed/entropy/rule design                                         |

---

## System Overview

**CAultron** is a cryptographic engine using a 1D cellular automaton. The rule is set by the first 8 bits of the derived seed. All entropy injection uses ChaCha20 output.

### Key-Derivation Steps

| Step | Description                                                                                 |
|------|---------------------------------------------------------------------------------------------|
| 1    | **Seed Derivation:** XOR of SHA-256 hashes of secrets (including a cryptographically secure random bitstring)                  |
| 2    | **Universe Initialization:** ChaCha20 CSPRNG, seed-based                                    |
| 3    | **CA Evolution:** Rule from seed, evolutions = (last 5 bits of seed × universe size)        |
| 4    | **Entropy Injection:** ChaCha20 output at each evolution                                    |
| 5    | **Key Output:** SHA-512 hash of final CA state                                              |

---

## Architecture Diagram

```mermaid
flowchart TD
    S[Secrets] --> SD[Seed Derivation]
    SD --> UI[Universe Initialization]
    UI --> CA[CA Evolution (Rule from Seed)]
    CA --> EI[Entropy Injection (ChaCha20)]
    EI --> KD[Key Derivation (SHA-512)]
    KD --> K[Key Output]
    CA -.-> Q[Quantum Attack]
    Q -.-> QS[No Speedup]
```

---

## Security Properties

| Property                    | Description |
|-----------------------------|-------------|
| Computational Irreducibility| CA evolution (rule from seed) requires actual computation; no shortcuts |
| Secret Dependence           | Each step uses a fresh seed from secrets |
| Entropy Conservation        | Universe resizing, relocation, and injection maintain entropy |
| Quantum Resistance          | No known quantum speedup for CA state prediction |

---

## Forward and Backward Secrecy

- Compromising a state or key at any step does **not** reveal previous or future states/keys.
- Keys are uncorrelated between derivation steps.
- Dual-point key derivation: output key is a function of two unpredictable points in CA evolution.

---

All mechanisms are deterministic and reproducible for the same inputs, with minimal memory footprint and high theoretical entropy.


## System Overview



CAultron is a cryptographic engine based on a 1D elementary cellular automaton, where the rule is dynamically selected by the first 8 bits of the derived seed (allowing any rule 0–255). The system uses a single universe. All seed injection and per-key-derivation-step entropy is performed via ChaCha20 output.

**Key-Derivation Process:**
To derive a single key, the CA state is initialized and then evolved through a key-derivation step. For each key-derivation step, the number of evolutions is determined by the last 5 bits of the seed (interpreted as n, with minimum 1) times the universe size. At each evolution, ChaCha20 output (derived from the seed and evolution index) is injected into the universe, followed by CA evolution. After all evolutions, the key is produced by hashing the CA state with SHA-512.

- Multi-secret, high-entropy seed derivation ([Spec 3](spec%203%20-%20Seed%20Derivation.md))
- Single-universe architecture ([Spec 2](spec%202%20-%20Data%20Types%20and%20Structure.md), [Spec 5](spec%205%20-%20Universe%20Evolution.md))
- ChaCha20-based noise initialization ([Spec 5](spec%205%20-%20Universe%20Evolution.md))
- Per-key-derivation-step entropy injection via ChaCha20 ([Spec 4](spec%204%20-%20Entropy%20Injection.md))
- Deterministic, irreversible CA evolution (rule determined by seed, [Spec 5](spec%205%20-%20Universe%20Evolution.md))
- Key derivation via SHA-512 after all evolutions ([Spec 6](spec%206%20-%20Key%20Derivation.md))
- Forward and backward secrecy ([Spec 7](spec%207%20-%20Forward%20and%20Backward%20Secrecy.md))
- Quantum resistance: CA evolution (rule selected by seed) requires actual computation; no shortcuts. No known quantum speedup for CA state prediction. Each step requires a fresh seed derived from secrets. Entropy is maintained by universe resizing, relocation, and injection.
### Quantum Resistance

| Property                    | Description |
|-----------------------------|-------------|
| Computational Irreducibility| CA evolution (rule selected by seed) requires actual computation; no shortcuts |
| Secret Dependence           | Each step requires a fresh seed derived from secrets |
| Entropy Conservation        | Universe resizing, relocation, and injection maintain minimum entropy |
| Quantum Resistance          | No known quantum speedup for CA state prediction |

```mermaid
flowchart TD
    A[Seed, State] --> B[CA Evolution (Rule selected by seed)]
    B --> C[Key Derivation]
    C --> D[Encryption]
    B -.-> E[Quantum Attack]
    E -.-> F[No Speedup]
```
- Systematic risk analysis ([Spec 10](spec%2010%20-%20Attack%20Scenarios%20and%20Mitigations.md))


All mechanisms are deterministic and reproducible for the same inputs, with a minimal memory footprint and high theoretical entropy. (Note: State verification is not part of the current CAultron design.)

### Architecture Overview
```mermaid
flowchart TD
    A[Multi-Secret Seed Derivation] --> B[ChaCha20 Noise Init]
    B --> C[Universe]
    C --> D[Key-Derivation Step: For each evolution (n × universe size)]
    D --> E[Inject ChaCha20 Entropy]
    E --> F[CA Evolution (Rule selected by seed)]
    F --> G[Repeat for all evolutions]
    G --> H[Final CA State]
    H --> I[SHA-512 Key Derivation]
    I --> J[Encryption Key]
    G --> J[State Verification]
```




### Forward and Backward Secrecy

CAultron110 provides strong forward and backward secrecy:
- Compromising a state or key at any step does not reveal previous or future states/keys, due to dynamic rule selection and per-evolution entropy injection.
- Keys are uncorrelated between derivation steps.
- The dual-point key derivation method ensures that the output key is a function of two unpredictable points in the CA evolution.
