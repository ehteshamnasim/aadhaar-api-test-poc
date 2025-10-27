"""
Quick demo to show self-healing in action
"""
import subprocess
import sys

print("=" * 70)
print("SELF-HEALING DEMONSTRATION")
print("=" * 70)
print()
print("ℹ️  Setup:")
print("   - Dummy API is returning status code 201 (instead of expected 200)")
print("   - Tests expect status code 200")
print("   - Tests will FAIL")
print("   - Self-healing will detect the failure and attempt to fix it")
print()
print("=" * 70)
print()

# Run a single test that will fail
print("Running test_verify_aadhaar_success...")
print()

result = subprocess.run(
    ['pytest', 'tests/test_aadhaar_api_v35.py::test_verify_aadhaar_success', '-v'],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print(result.stderr)

print()
print("=" * 70)
if result.returncode != 0:
    print("✅ Test failed as expected (status code mismatch: 200 vs 201)")
    print("🔧 This should trigger self-healing in main.py")
    print()
    print("To see self-healing in action, commit your YAML file:")
    print("   git add specs/aadhaar-api.yaml")
    print("   git commit -m 'test self-healing'")
else:
    print("⚠️  Test passed - self-healing won't trigger")
print("=" * 70)
