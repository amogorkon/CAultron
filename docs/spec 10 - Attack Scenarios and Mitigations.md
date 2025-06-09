# 10. Attack Scenarios and Mitigations (FMEA)

# 10. Attack Scenarios and Mitigations (FMEA)

| FM/AS   | Effect/Impact                | Cause/Vector                                                                 | S | O | D | RPN | Controls/Mitig.         | S' | O' | D' | RR |
|---------|------------------------------|-------------------------------------------------------------------------------|---|---|---|-----|-------------------------|----|----|----|----|
| KS+KS   | Compute $S_{i+1}$, $K_{i+1}$ | Compromise of CA state and next seed (e.g., memory scraping + secret access)  | 6 | 2 | 3 | 36  | Mem+sec encl, enc mem   | 3  | 1  | 2  | 6   |
| IPI     | Target block by iter guess   | Predictable or leaked iteration count                                         | 4 | 3 | 5 | 60  | Hash idx in seed        | 2  | 1  | 3  | 6   |
| EIA     | Reveal inj. patterns         | Large sample of ciphertexts, weak randomness                                  | 2 | 2 | 5 | 20  | Hi-ent, uniq seed, pad  | 1  | 1  | 3  | 3   |
| ST      | Mod CA state undetected      | Memory corruption or malicious actor modifies CA state                        | 6 | 2 | 5 | 60  | Hash in block header    | 2  | 1  | 2  | 4   |
| SCA     | Secret leak (timing, power)  | Physical access or advanced analysis (timing, power, EM, cache, etc.)         | 6 | 1 | 1 | 6   | CT ops, sec mem, hw     | 3  | 1  | 2  | 6   |
| BFS     | Key recovery by brute force  | Weak password or low entropy in secrets                                       | 6 | 2 | 5 | 60  | Strong pw, hi iter      | 2  | 1  | 3  | 6   |
| PSD     | Brute-force if 1 secret weak | One secret (password, timestamp, or iteration) is weak or compromised         | 6 | 2 | 3 | 36  | Multi hi-ent secrets    | 2  | 1  | 2  | 4   |
| RA      | Replay old seeds/blocks      | Reuse of timestamps or block indices enables replay of encrypted blocks       | 4 | 2 | 5 | 40  | Nonce/counter in seed   | 1  | 1  | 2  | 2   |
| SMA     | Manipulate seed inputs       | Input tampering or weak input validation allows attacker to control evolution | 6 | 2 | 5 | 60  | Validate, protect seed  | 2  | 1  | 2  | 4   |
| WR      | Predictable evolution        | Non-unique or predictable timestamps/iterations                              | 6 | 2 | 5 | 60  | CSPRNG, SHA-512         | 2  | 1  | 2  | 4   |
| KSR     | Cross-block key/seed reuse   | Not including unique block data in seed enables cross-block attacks           | 6 | 2 | 5 | 60  | Unique block in seed    | 2  | 1  | 2  | 4   |

Legend:
- FM/AS: Failure Mode / Attack Scenario (KS+KS: Known State + Known Seed, IPI: Iteration Prediction, EIA: Entropy Injection Analysis, ST: State Tampering, SCA: Side-Channel Attack, BFS: Brute-Force Search, PSD: Partial Secret Disclosure, RA: Replay Attack, SMA: Seed Manipulation, WR: Weak Randomness, KSR: Key/Seed Reuse)
- S, O, D: Severity, Occurrence, Detection (before mitigation; 1=lowest, 6=highest)
- RPN: Risk Priority Number before mitigation (S × O × D)
- S', O', D': Severity, Occurrence, Detection (after mitigation; 1=lowest, 6=highest)
- RR: Residual Risk (S' × O' × D', after mitigation)
- Controls/Mitig.: Main mitigation or control applied
