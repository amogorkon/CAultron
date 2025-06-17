

# 6. Key Derivation: Dual Point Derivation


## Overview: Dual Point Derivation

CAultron uses a "Dual Point Derivation" method for key generation. This approach leverages a single-universe CA, dynamic meta-rule selection, and a random evolution index for pre-final key extraction. The process is as follows:


| Step      | Description |
|-----------|-------------|
| Evolution | CA evolves for N steps, each with a meta-rule selected from seed bits |
| Pre-final (First Point) | At evolution where (evolution index mod value of seed bits [-10:-5]) == 0, hash CA state with SHA-512 (pre-final key) |
| Final (Second Point)    | After all evolutions, hash final CA state with SHA-512 (final key) |
| Output (Dual Point)     | XOR pre-final and final hashes to produce the derived encryption key |


This Dual Point Derivation method ensures that the output key is a function of two unpredictable points in the CA evolution: a random pre-final point and the final state. The meta-rule for each evolution is encoded using 28 bits from the seed (see [Spec 4]). The number of evolutions and the pre-final key index are also determined by seed bits, ensuring unpredictability. State verification is not part of the current design.

| Step      | Description |
|-----------|-------------|
| Evolution | CA evolves for N iterations |
| Hashing   | Hash final CA state with SHA-512 |
| Output    | Use digest as derived encryption key |



```mermaid
flowchart TD
    A[CA State Evolution (meta-rule per step)] --> B[First Point: SHA-512 at random evolution (pre-final)]
    A --> C[Second Point: SHA-512 after last evolution (final)]
    B & C --> D[XOR (Dual Point Derivation)]
    D --> E[Encryption Key]
```
