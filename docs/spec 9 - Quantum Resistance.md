# 9. Quantum Resistance

| Property                    | Description |
|-----------------------------|-------------|
| Computational Irreducibility| Rule 110 evolution requires actual computation; no shortcuts |
| Secret Dependence           | Each step requires a fresh seed derived from secrets |
| Entropy Conservation        | Universe resizing, relocation, and injection maintain minimum entropy |
| Quantum Resistance          | No known quantum speedup for CA state prediction |

```mermaid
flowchart TD
    A[Seed, State] --> B[CA Evolution (Rule 110)]
    B --> C[Key Derivation]
    C --> D[Encryption]
    B -.-> E[Quantum Attack]
    E -.-> F[No Speedup]
```
