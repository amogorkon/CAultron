
# 10. Attack Scenarios and Mitigations (FMEA)

## Overview


This section analyzes attack scenarios and mitigations for the CAultron system, now featuring:
- A single-universe cellular automaton architecture
- Dynamic meta-rule encoding and per-evolution rule selection (see [Spec 4])
- Randomized evolution count and Dual Point Derivation for key extraction (see [Spec 5], [Spec 6])
- Key output as XOR of pre-final and final universe hashes (Dual Point Derivation)

The meta-rule system and random evolution index (derived from seed bits) significantly increase the attack surface complexity, making brute-force and prediction attacks far less feasible. Dual Point Derivation ensures that the derived key is a function of two unpredictable points in the CA evolution.

# 10. Attack Scenarios and Mitigations (FMEA)


| FM/AS   | Effect/Impact                | Cause/Vector                                                                 | S | O | D | RPN | Controls/Mitig.         | S' | O' | D' | RR |
|---------|------------------------------|-------------------------------------------------------------------------------|---|---|---|-----|-------------------------|----|----|----|----|
| KS+KS   | Compute $S_{i+1}$, $K_{i+1}$ | Compromise of CA state and next seed (e.g., memory scraping + secret access)  | 6 | 2 | 3 | 36  | Mem+sec encl, enc mem   | 3  | 1  | 2  | 6   |
| IPI     | Target block by iter guess   | Predictable or leaked evolution count or random index                         | 4 | 3 | 5 | 60  | Hash idx in seed, randomize via seed bits | 2  | 1  | 3  | 6   |
| EIA     | Reveal inj. patterns         | Large sample of ciphertexts, weak randomness                                  | 2 | 2 | 5 | 20  | Hi-ent, uniq seed, pad  | 1  | 1  | 3  | 3   |
| ST      | Mod CA state undetected      | Memory corruption or malicious actor modifies CA state                        | 6 | 2 | 5 | 60  | Hash in block header    | 2  | 1  | 2  | 4   |
| SCA     | Secret leak (timing, power)  | Physical access or advanced analysis (timing, power, EM, cache, etc.)         | 6 | 1 | 1 | 6   | CT ops, sec mem, hw     | 3  | 1  | 2  | 6   |
| BFS     | Key recovery by brute force  | Weak password or low entropy in secrets                                       | 6 | 2 | 5 | 60  | Strong pw, hi iter, dynamic meta-rule | 2  | 1  | 3  | 6   |
| PSD     | Brute-force if 1 secret weak | One secret (password, timestamp, or iteration) is weak or compromised         | 6 | 2 | 3 | 36  | Multi hi-ent secrets    | 2  | 1  | 2  | 4   |
| RA      | Replay old seeds/blocks      | Reuse of timestamps or block indices enables replay of encrypted blocks       | 4 | 2 | 5 | 40  | Nonce/counter in seed   | 1  | 1  | 2  | 2   |
| SMA     | Manipulate seed inputs       | Input tampering or weak input validation allows attacker to control evolution | 6 | 2 | 5 | 60  | Validate, protect seed, meta-rule bits | 2  | 1  | 2  | 4   |
| WR      | Predictable evolution        | Non-unique or predictable timestamps/iterations or static rule set            | 6 | 2 | 5 | 60  | CSPRNG, SHA-512, dynamic meta-rule | 2  | 1  | 2  | 4   |
| KSR     | Cross-block key/seed reuse   | Not including unique block data in seed enables cross-block attacks           | 6 | 2 | 5 | 60  | Unique block in seed    | 2  | 1  | 2  | 4   |
| MRE     | Meta-rule exposure/guess     | Attacker learns or guesses meta-rule encoding or rule schedule                | 6 | 1 | 5 | 30  | Randomize rule per evolution, seed-derived meta-rule, 28-bit space | 2  | 1  | 2  | 4   |
| RPI     | Pre-final key index predict  | Attacker predicts or controls pre-final evolution index                       | 5 | 2 | 5 | 50  | Derive index from seed bits, keep bits secret | 2  | 1  | 2  | 4   |
| XFK     | Final/pre-final key XOR leak | Weakness in XOR or hash function exposes key material                         | 6 | 1 | 5 | 30  | Use SHA-512, strong hash, never reuse state | 2  | 1  | 2  | 4   |

Legend:
- FM/AS: Failure Mode / Attack Scenario
    - KS+KS: Known State + Known Seed
    - IPI: Iteration/Evolution Prediction (now includes random evolution index)
    - EIA: Entropy Injection Analysis
    - ST: State Tampering
    - SCA: Side-Channel Attack
    - BFS: Brute-Force Search
    - PSD: Partial Secret Disclosure
    - RA: Replay Attack
    - SMA: Seed Manipulation
    - WR: Weak Randomness or Static Rule
    - KSR: Key/Seed Reuse
    - MRE: Meta-Rule Exposure/Guessing (new: dynamic rule encoding)
    - RPI: Random Pre-final Index Prediction (new: pre-final key extraction)
    - XFK: XOR Final Key Weakness (new: final/pre-final key XOR)
- S, O, D: Severity, Occurrence, Detection (before mitigation; 1=lowest, 6=highest)
- RPN: Risk Priority Number before mitigation (S × O × D)
- S', O', D': Severity, Occurrence, Detection (after mitigation; 1=lowest, 6=highest)
- RR: Residual Risk (S' × O' × D', after mitigation)
- Controls/Mitig.: Main mitigation or control applied
