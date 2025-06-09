# 3. Seed Derivation

| Input      | Operation                | Output |
|------------|--------------------------|--------|
| Password1  | SHA-256                  | H1     |
| Password2  | SHA-256                  | H2     |
| other secrets | SHA-256               | H5     |
| Timestamp  | SHA-256                  | H3     |
| Iteration  | SHA-256                  | H4     |
| H1, H2, H3, (H4) | XOR                | Seed   |

```mermaid
flowchart TD
    A[Password1] --> B[SHA-256]
    C[Password2] --> D[SHA-256]
    E[Timestamp] --> F[SHA-256]
    G[Iteration] --> H[SHA-256]
    I[Passkey] --> J[SHA-256]
    K[Other Secrets] --> L[SHA-256]
    B --> M[XOR]
    D --> M
    F --> M
    H --> M
    J --> M
    L --> M
    M --> N[Seed]
```

**Security Note:**
At least two secrets must be strong and confidential. If only one is unknown, brute-force is possible. With two or more unknown, recovery is infeasible. XOR allows any number of secrets in any order.
