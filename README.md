
# CAultron

## 🧬 Quantum-Inspired, Adaptive Cryptographic Cellular Automaton

CAultron is a cryptographic key derivation and analysis toolkit based on a 1D cellular automaton (CA) with adaptive, entropy-driven evolution. It is designed for research, security, and educational use.

### Key Features

- **Adaptive CA Evolution:**
  - The CA's rule bits are mutated if the entropy change between steps is too small, ensuring persistent complexity and avoiding trivial attractors without reducing the number of possible rules an attacker would have to try while requiring non-trivial computation per step.
- **Entropy Injection:**
  - The seed (derived from secrets, public salt and counter) is injected via chacha20 into the CA state before every evolution step to avoid stagnation and ensure high entropy at every step.
- **Dual Point Derivation:**
  - Two numbers of iterations are determined from the seed bits: middle and end. The CA is evolved until the middle iteration, from which a full SHA-512 is calculated from the state. The CA then is evolved until the end iteration, from which a SHA-512 is calculated from the final state. The key then is calculated as the XOR of both hashes. This requires an attacker to compute all steps with no shortcuts, calculating and storing the hashes for all steps in order to try to find a key, which is computationally expensive.
  - Trying to precompute keys is quantum-hard because the CA is evolved in a way that requires the attacker to compute all steps in order, and the key is derived from some middle and the final state, which is not known until all steps are completed.
- **Forward and Backward Security:**
  - Since the counter is also used as part of the seed for each step, each key derivation is unique to the counter, making it resistant to precomputation attacks and forward and backward security is provided.
  - Guessing one key correctly does not help in guessing other keys as the counter is part of the seed and the CA evolution is unique for each counter value.



## 🚀 Quickstart

### Install

```bash
pip install caultron
```


## 🧠 The Algorithm

- The secrets and counter are hashed and xor-ed with the public salt to produce a 32-byte seed.
- At each step, entropy is injected into the CA state using chacha20, ensuring continuous high entropy.
- From the left of the seed, the rules are derived and from the right of the seed two iteration counts are derived: one for the middle and one for the end of the CA evolution.
- The CA is evolved for as many steps as the middle iteration count, and a SHA-512 hash is computed from the state at that point.
- The CA is then evolved for as many steps as the end iteration count, and another SHA-512 hash is computed from the final state.
- The final key is derived by XOR-ing both hashes together.
- Every step of the CA evolution, the Shannon entropy of the CA state is calculated and compared between steps - if the entropy change is too small, the rule bits are mutated to ensure the CA continues to evolve in a complex manner.

## 📄 License

MIT License. See LICENSE file.
