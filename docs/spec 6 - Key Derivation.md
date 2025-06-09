# 6. Key Derivation

| Step      | Description |
|-----------|-------------|
| Evolution | CA evolves for N iterations |
| Hashing   | Hash final CA state with SHA-512 |
| Output    | Use digest as derived encryption key |

```mermaid
flowchart TD
    A[CA State Evolution] --> B[SHA-512 Hash]
    B --> C[Encryption Key]
```
