#!/usr/bin/env python3
"""
zkComply MVP - Command Line Interface
Interactive tool for generating and verifying ZK proofs
"""

import argparse
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from zkcomply_mvp import ZKComplyMVP

def generate_proof_cli(args):
    """Generate ZK proof via CLI"""
    print(f"🔐 Generating ZK proof for {args.name}...")

    # Initialize system
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)

    # Generate proof
    proof = zk_system.generate_proof(args.name, args.dob)

    # Save proof if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(proof, f, indent=2)
        print(f"💾 Proof saved to {args.output}")

    # Display result
    if proof['proof_valid']:
        print(f"✅ SUCCESS: {args.name} is NOT sanctioned")
        print(f"🔑 Proof hash: {proof['zk_proof']}")
    else:
        print(f"❌ REJECTED: {args.name} appears to be sanctioned")

    if args.verbose:
        print(f"\n📋 Proof Details:")
        print(f"   • User hash: {proof['user_hash'][:20]}...")
        print(f"   • Merkle root: {proof['merkle_root'][:20]}...")
        print(f"   • Timestamp: {proof['timestamp']}")
        print(f"   • System: {proof['system']}")

def verify_proof_cli(args):
    """Verify ZK proof via CLI"""
    print(f"🔍 Verifying proof from {args.proof}...")

    # Load proof
    with open(args.proof, 'r') as f:
        proof_data = json.load(f)

    # Initialize system
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)

    # Verify proof
    is_valid = zk_system.verify_proof(proof_data)

    if is_valid:
        print(f"✅ PROOF VALID: User is confirmed NOT sanctioned")
    else:
        print(f"❌ PROOF INVALID: Verification failed")

    if args.verbose:
        print(f"\n📋 Verification Details:")
        print(f"   • Proof hash: {proof_data['zk_proof']}")
        print(f"   • Merkle root match: {proof_data['merkle_root'][:20]}...")
        print(f"   • Sanctioned status: {proof_data['is_sanctioned']}")

def list_sanctioned_cli(args):
    """List sanctioned entities"""
    print("📋 Currently sanctioned entities:")

    data_path = os.path.join(os.path.dirname(__file__), 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)

    for i, entry in enumerate(zk_system.ofac_data, 1):
        print(f"   {i}. {entry['name']} (DOB: {entry['dob']}) - {entry['program']}")

def system_info_cli(args):
    """Display system information"""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)
    info = zk_system.get_system_info()

    print("📊 zkComply System Information")
    print("=" * 40)
    for key, value in info.items():
        if key == 'merkle_root':
            print(f"{key}: {value[:20]}...")
        else:
            print(f"{key}: {value}")

def main():
    parser = argparse.ArgumentParser(description='zkComply MVP - Zero-Knowledge OFAC Compliance')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate proof command
    generate_parser = subparsers.add_parser('prove', help='Generate ZK proof')
    generate_parser.add_argument('--name', required=True, help='User full name')
    generate_parser.add_argument('--dob', required=True, help='Date of birth (YYYY-MM-DD)')
    generate_parser.add_argument('--output', help='Save proof to file')
    generate_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    generate_parser.set_defaults(func=generate_proof_cli)

    # Verify proof command
    verify_parser = subparsers.add_parser('verify', help='Verify ZK proof')
    verify_parser.add_argument('--proof', required=True, help='Path to proof file')
    verify_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    verify_parser.set_defaults(func=verify_proof_cli)

    # List sanctioned command
    list_parser = subparsers.add_parser('list', help='List sanctioned entities')
    list_parser.set_defaults(func=list_sanctioned_cli)

    # System info command
    info_parser = subparsers.add_parser('info', help='System information')
    info_parser.set_defaults(func=system_info_cli)

    # Parse and execute
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    try:
        args.func(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
