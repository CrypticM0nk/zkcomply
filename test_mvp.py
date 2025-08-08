#!/usr/bin/env python3
"""
zkComply MVP - Test Suite
Automated testing for hackathon demo
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from zkcomply_mvp import ZKComplyMVP

def test_system_initialization():
    """Test system can initialize properly"""
    print("🧪 Testing system initialization...")

    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)

    assert len(zk_system.ofac_data) > 0, "OFAC data should be loaded"
    assert len(zk_system.sanctioned_hashes) > 0, "Sanctioned hashes should be generated"
    assert zk_system.merkle_root != "0" * 64, "Merkle root should be computed"

    print("✅ System initialization test passed")

def test_non_sanctioned_user():
    """Test that non-sanctioned user gets valid proof"""
    print("🧪 Testing non-sanctioned user...")

    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)

    # Test Alice Johnson (not in sanctions list)
    proof = zk_system.generate_proof("Alice Johnson", "1992-03-15")
    is_verified = zk_system.verify_proof(proof)

    assert not proof['is_sanctioned'], "Alice should not be sanctioned"
    assert proof['proof_valid'], "Proof should be valid"
    assert is_verified, "Proof should verify successfully"
    assert proof['system'] == "zkComply", "System should be zkComply"

    print("✅ Non-sanctioned user test passed")

def test_sanctioned_user():
    """Test that sanctioned user cannot get valid proof"""
    print("🧪 Testing sanctioned user...")

    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)

    # Test Putin (in sanctions list)
    proof = zk_system.generate_proof("VLADIMIR PUTIN", "1952-10-07")
    is_verified = zk_system.verify_proof(proof)

    assert proof['is_sanctioned'], "Putin should be sanctioned"
    assert not proof['proof_valid'], "Proof should not be valid"
    assert not is_verified, "Proof should not verify"

    print("✅ Sanctioned user test passed")

def test_proof_consistency():
    """Test that proofs are consistent"""
    print("🧪 Testing proof consistency...")

    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ofac_sanctions.csv')
    zk_system = ZKComplyMVP(data_path)

    # Generate same proof twice
    proof1 = zk_system.generate_proof("Bob Smith", "1985-07-20")
    proof2 = zk_system.generate_proof("Bob Smith", "1985-07-20")

    assert proof1['user_hash'] == proof2['user_hash'], "Same user should have same hash"
    assert proof1['zk_proof'] == proof2['zk_proof'], "Same user should have same proof"

    print("✅ Proof consistency test passed")

def run_all_tests():
    """Run all tests"""
    print("🚀 zkComply MVP Test Suite")
    print("=" * 40)

    tests = [
        test_system_initialization,
        test_non_sanctioned_user,
        test_sanctioned_user,
        test_proof_consistency
    ]

    passed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
        print()

    print(f"📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed! zkComply system ready for demo.")
        return True
    else:
        print("❌ Some tests failed. Check implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
