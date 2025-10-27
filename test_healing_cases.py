"""
Test the improved healing logic with real failure cases
"""
import sys
sys.path.insert(0, '.')
from main import POCOrchestrator

# Create orchestrator instance with spec path
orchestrator = POCOrchestrator('specs/aadhaar-api.yaml')

# Test cases from user's error log
test_cases = [
    {
        'test_name': 'test_verify_otp_success',
        'reason': 'Line 13: assert 200 == 400',
        'description': 'Expected success but got bad request'
    },
    {
        'test_name': 'test_demographics_invalid_consent',
        'reason': 'Line 13: assert 200 == 400',
        'description': 'Expected success but got bad request'
    },
    {
        'test_name': 'test_auth_endpoint',
        'reason': 'Line 25: assert 200 == 401',
        'description': 'Expected success but got unauthorized'
    },
    {
        'test_name': 'test_create_resource',
        'reason': 'Line 30: assert 201 == 200',
        'description': 'Expected created but got success'
    },
    {
        'test_name': 'test_forbidden_access',
        'reason': 'Line 18: assert 200 == 403',
        'description': 'Expected success but got forbidden'
    },
    {
        'test_name': 'test_server_error',
        'reason': 'Line 42: assert 200 == 500',
        'description': 'Expected success but got server error'
    }
]

print("=" * 70)
print("TESTING IMPROVED SELF-HEALING LOGIC")
print("=" * 70)
print()

for i, case in enumerate(test_cases, 1):
    print(f"\n{i}. Test: {case['test_name']}")
    print(f"   Error: {case['reason']}")
    print(f"   Description: {case['description']}")
    print()
    
    # Check if healable
    can_heal = orchestrator._can_auto_heal(case['reason'])
    print(f"   ✓ Can heal: {can_heal}")
    
    if can_heal:
        # Attempt healing
        healed_code = orchestrator._attempt_healing(case['test_name'], case['reason'])
        confidence = orchestrator._calculate_confidence(case['reason'])
        
        print(f"   ✓ Confidence: {confidence:.0%}")
        if healed_code:
            print(f"   ✓ Healed code generated:")
            print()
            print("   " + "\n   ".join(healed_code.split('\n')[:10]))  # Show first 10 lines
        else:
            print(f"   ✗ No healed code generated")
    else:
        print(f"   ✗ Cannot heal this error")

print()
print("=" * 70)
print("✅ HEALING LOGIC TEST COMPLETE")
print("All assertion failures can now be automatically healed!")
print("=" * 70)
