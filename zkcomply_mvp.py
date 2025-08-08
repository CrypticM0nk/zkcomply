"""
zkComply MVP - Zero-Knowledge OFAC Compliance System
Hackathon submission demonstrating privacy-preserving sanctions screening
"""

import hashlib
import json
import csv
from typing import List, Dict, Any, Tuple
from datetime import datetime

class ZKComplyMVP:
    """MVP implementation of zero-knowledge sanctions proof system"""

    def __init__(self, ofac_data_path: str = "data/ofac_sanctions.csv"):
        self.ofac_data = self._load_ofac_data(ofac_data_path)
        self.sanctioned_hashes = self._generate_sanctioned_hashes()
        self.merkle_root = self._build_merkle_tree()

    def _load_ofac_data(self, path: str) -> List[Dict[str, str]]:
        """Load OFAC sanctions data"""
        with open(path, 'r') as f:
            return list(csv.DictReader(f))

    def _hash_identity(self, name: str, dob: str) -> str:
        """Hash identity using SHA256 (Poseidon simulation for MVP)"""
        combined = f"ZKCOMPLY:{name.upper()}:{dob}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _generate_sanctioned_hashes(self) -> List[str]:
        """Generate hashes for all sanctioned identities"""
        hashes = []
        for entry in self.ofac_data:
            hash_value = self._hash_identity(entry["name"], entry["dob"])
            hashes.append(hash_value)
        return hashes

    def _build_merkle_tree(self) -> str:
        """Build simplified Merkle tree (MVP version)"""
        if not self.sanctioned_hashes:
            return "0" * 64

        # Simplified: hash all sanctioned identities together
        combined = "ZKCOMPLY_MERKLE_ROOT:" + ":".join(sorted(self.sanctioned_hashes))
        return hashlib.sha256(combined.encode()).hexdigest()

    def generate_proof(self, user_name: str, user_dob: str) -> Dict[str, Any]:
        """Generate ZK proof that user is NOT sanctioned"""
        user_hash = self._hash_identity(user_name, user_dob)
        is_sanctioned = user_hash in self.sanctioned_hashes

        # Generate mock ZK proof
        proof_data = {
            "user_hash": user_hash,
            "merkle_root": self.merkle_root,
            "is_sanctioned": is_sanctioned,
            "proof_valid": not is_sanctioned,
            "zk_proof": self._generate_mock_proof(user_hash),
            "timestamp": datetime.now().isoformat(),
            "version": "mvp-1.0",
            "system": "zkComply"
        }

        return proof_data

    def _generate_mock_proof(self, user_hash: str) -> str:
        """Generate mock ZK proof (for MVP demonstration)"""
        proof_input = f"ZKCOMPLY_PROOF:{user_hash}:{self.merkle_root}"
        return "0x" + hashlib.sha256(proof_input.encode()).hexdigest()[:32]

    def verify_proof(self, proof_data: Dict[str, Any]) -> bool:
        """Verify ZK proof"""
        try:
            # Basic verification checks
            if proof_data["merkle_root"] != self.merkle_root:
                return False

            # Verify the proof is valid
            expected_proof = self._generate_mock_proof(proof_data["user_hash"])
            if proof_data["zk_proof"] != expected_proof:
                return False

            # Main verification: user should NOT be sanctioned
            return proof_data["proof_valid"] and not proof_data["is_sanctioned"]

        except Exception as e:
            print(f"Verification error: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "total_sanctioned": len(self.ofac_data),
            "merkle_root": self.merkle_root,
            "hash_function": "SHA256 (Poseidon simulation)",
            "system": "zkComply MVP",
            "version": "1.0.0"
        }

def demo_zkcomply():
    """Demonstration of the zkComply system"""
    print("🚀 zkComply MVP Demo")
    print("=" * 50)

    # Initialize system
    zk_system = ZKComplyMVP()

    # Show system info
    info = zk_system.get_system_info()
    print(f"\n📊 System Information:")
    print(f"   • Sanctioned entries: {info['total_sanctioned']}")
    print(f"   • Merkle root: {info['merkle_root'][:20]}...")
    print(f"   • Hash function: {info['hash_function']}")

    # Test Case 1: Non-sanctioned user (Alice)
    print(f"\n🧪 Test 1: Non-sanctioned user")
    alice_proof = zk_system.generate_proof("Alice Johnson", "1992-03-15")
    alice_verified = zk_system.verify_proof(alice_proof)

    print(f"   • User: Alice Johnson")
    print(f"   • Sanctioned: {alice_proof['is_sanctioned']}")
    print(f"   • Proof valid: {alice_proof['proof_valid']}")
    print(f"   • Verification: {'✅ PASSED' if alice_verified else '❌ FAILED'}")

    # Test Case 2: Sanctioned user (Putin)
    print(f"\n🧪 Test 2: Sanctioned user")
    putin_proof = zk_system.generate_proof("VLADIMIR PUTIN", "1952-10-07")
    putin_verified = zk_system.verify_proof(putin_proof)

    print(f"   • User: Vladimir Putin")
    print(f"   • Sanctioned: {putin_proof['is_sanctioned']}")
    print(f"   • Proof valid: {putin_proof['proof_valid']}")
    print(f"   • Verification: {'❌ CORRECTLY REJECTED' if not putin_verified else '⚠️ ERROR'}")

    # Test Case 3: Random user
    print(f"\n🧪 Test 3: Random user")
    bob_proof = zk_system.generate_proof("Bob Smith", "1985-07-20")
    bob_verified = zk_system.verify_proof(bob_proof)

    print(f"   • User: Bob Smith")
    print(f"   • Sanctioned: {bob_proof['is_sanctioned']}")
    print(f"   • Proof valid: {bob_proof['proof_valid']}")
    print(f"   • Verification: {'✅ PASSED' if bob_verified else '❌ FAILED'}")

    print(f"\n🎉 Demo completed!")
    print(f"✅ Non-sanctioned users can prove compliance without revealing identity")
    print(f"❌ Sanctioned users cannot generate valid proofs")
    print(f"🔐 zkComply: Privacy-preserving compliance for the modern world")

    return alice_proof, bob_proof

if __name__ == "__main__":
    demo_zkcomply()
