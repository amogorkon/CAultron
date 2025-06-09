# 5. Universe Evolution

| Component         | Description |
|-------------------|-------------|
| Outer Universe    | Fixed-size array (e.g., 1024 cells) defines the full canvas; astronomical state space; compact bit-level storage. |
| Inner Universe    | Dynamic, variable-size active region; size determined by seed; boundaries change per iteration for obfuscation. |
| Dynamic Padding   | Maximum array size is dynamically reduced based on seed per iteration; deters reverse-engineering. |
| ChaCha20 Init     | Universe pre-initialized with ChaCha20 CSPRNG using seed-derived key and nonce; ensures high-entropy, noise-filled start. |
| Evolution         | Rule 110 CA evolves every iteration, applying transition rules to produce a new state. |
| Resizing          | Inner universe size and position are dynamic, derived from the seed. |
| Irreversibility   | Entropy injection and dynamic sizing make reversal impossible. |
| Impact            | Variable inner universe increases key space; noise-filled init prevents weak states; deterministic and reproducible; minimal memory footprint. |

```mermaid
flowchart TD
    A[Seed Derivation] --> B[ChaCha20 Init (Noise)]
    B --> C[Outer Universe]
    C --> D[Inner Universe Sizing]
    D --> E[CA Evolution (Rule 110)]
    E --> F[Dynamic Padding/Adjustment]
    F --> G[Final CA State]
```
