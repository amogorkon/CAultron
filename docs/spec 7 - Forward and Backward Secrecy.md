# 7. Forward and Backward Secrecy

| Property            | Description |
|---------------------|-------------|
| Forward Secrecy     | Compromising $S_i$ does not reveal $S_{i+1}$ without $seed_{i+1}$; $S_{i+1} = evolve(S_i, seed_{i+1})$ |
| Backward Secrecy    | Previous states unrecoverable due to entropy injection; $S_{i-1} \nLeftarrow S_i$ |
| Key Independence    | Keys are uncorrelated due to iterative entropy injection |

```mermaid
flowchart TD
    A[Current State S_i] --> B[Next State S_{i+1}]
    B --> C[Key Derivation]
    A -.-> D[Previous State S_{i-1}]
    D -.-> C
```
