from .ca import derive_key, prepare_secrets

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="CAultron: Quantum-inspired CA key derivation."
    )
    parser.add_argument(
        "--password", type=str, required=True, help="Password or secret"
    )
    parser.add_argument("--salt", type=str, required=True, help="Salt (hex or string)")
    parser.add_argument("--counter", type=int, default=1, help="Iteration counter")
    parser.add_argument("--size", type=int, default=1024, help="Universe size")
    args = parser.parse_args()

    secrets = prepare_secrets(args.password)
    try:
        salt = bytes.fromhex(args.salt)
    except ValueError:
        salt = args.salt.encode()
    key = derive_key(secrets, salt, args.counter, size=args.size)
    print(key.hex())
