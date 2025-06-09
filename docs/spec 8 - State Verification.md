# 8. State Verification

| Step         | Description |
|--------------|-------------|
| Fingerprint  | Store a hash of the CA state at each iteration for verification |
| Verify       | Compare current state hash to stored fingerprint to detect tampering |

```mermaid
flowchart TD
    A[CA State] --> B[Hash (Fingerprint)]
    B --> C[Store/Compare]
    C --> D[Verification Result]
```

**Purpose:**
- Detects tampering or corruption of CA state
