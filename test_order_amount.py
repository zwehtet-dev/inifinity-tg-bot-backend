"""
Test script to verify backend API correctly accepts and stores order amounts.

This test sends order submissions with various amounts to ensure the backend
properly handles numeric values and doesn't default to 0.0.
"""
import requests
import json
import io
from PIL import Image

# Backend API configuration
BASE_URL = "http://localhost:5000"
SUBMIT_ORDER_URL = f"{BASE_URL}/api/orders/submit"

def create_dummy_image():
    """Create a dummy image for testing."""
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_order_submission(test_name, amount, price, order_type="buy", chat_id="2060245779"):
    """
    Test order submission with specific amount.
    
    Args:
        test_name: Name of the test case
        amount: Amount to test
        price: Exchange rate/price
        order_type: "buy" or "sell"
        chat_id: Telegram chat ID
    """
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*80}")
    print(f"📊 Input Data:")
    print(f"   - Amount: {amount} (type: {type(amount).__name__})")
    print(f"   - Price: {price} (type: {type(price).__name__})")
    print(f"   - Order Type: {order_type}")
    print(f"   - Chat ID: {chat_id}")
    
    # Prepare form data
    form_data = {
        'order_type': order_type,
        'amount': str(amount),  # Convert to string as form data
        'price': str(price),
        'chat_id': chat_id,
        'user_bank': 'KBZ Bank - 1234567890 - Test User'
    }
    
    # Prepare file
    files = {
        'receipt': ('test_receipt.png', create_dummy_image(), 'image/png')
    }
    
    try:
        # Send POST request
        print(f"\n📤 Sending POST request to {SUBMIT_ORDER_URL}")
        response = requests.post(
            SUBMIT_ORDER_URL,
            data=form_data,
            files=files,
            timeout=10
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"\n📋 Response Data:")
            print(json.dumps(result, indent=2))
            
            # Verify amount
            returned_amount = result.get('order', {}).get('amount')
            print(f"\n🔍 Amount Verification:")
            print(f"   - Sent: {amount}")
            print(f"   - Received: {returned_amount}")
            
            if returned_amount == amount:
                print(f"   ✅ PASS: Amount matches!")
            elif returned_amount == 0.0:
                print(f"   ❌ FAIL: Amount is 0.0 (BUG DETECTED!)")
            else:
                print(f"   ⚠️  WARNING: Amount mismatch!")
            
            return True, result
        else:
            print(f"❌ FAILED!")
            print(f"Response: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to backend at {BASE_URL}")
        print(f"   Make sure the backend server is running on port 5000")
        return False, None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None

def run_all_tests():
    """Run all test cases."""
    print("\n" + "="*80)
    print("🚀 BACKEND ORDER AMOUNT TEST SUITE")
    print("="*80)
    print("\nThis test verifies that the backend API correctly accepts and stores")
    print("order amounts without defaulting to 0.0")
    
    test_cases = [
        {
            "name": "Standard Buy Order - Integer Amount",
            "amount": 1213.0,
            "price": 125.78,
            "order_type": "buy"
        },
        {
            "name": "Buy Order - Decimal Amount",
            "amount": 1500.50,
            "price": 125.78,
            "order_type": "buy"
        },
        {
            "name": "Sell Order - Large Amount",
            "amount": 500000.0,
            "price": 123.6,
            "order_type": "sell"
        },
        {
            "name": "Buy Order - Small Amount",
            "amount": 100.25,
            "price": 125.78,
            "order_type": "buy"
        },
        {
            "name": "Edge Case - Very Small Amount",
            "amount": 0.01,
            "price": 125.78,
            "order_type": "buy"
        }
    ]
    
    results = []
    for test_case in test_cases:
        success, result = test_order_submission(
            test_name=test_case["name"],
            amount=test_case["amount"],
            price=test_case["price"],
            order_type=test_case["order_type"]
        )
        results.append({
            "test": test_case["name"],
            "success": success,
            "amount_sent": test_case["amount"],
            "amount_received": result.get('order', {}).get('amount') if result else None
        })
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results if r["success"] and r["amount_sent"] == r["amount_received"])
    failed = len(results) - passed
    
    for result in results:
        status = "✅ PASS" if result["success"] and result["amount_sent"] == result["amount_received"] else "❌ FAIL"
        print(f"{status} - {result['test']}")
        if result["amount_received"] is not None:
            print(f"         Sent: {result['amount_sent']}, Received: {result['amount_received']}")
    
    print(f"\n{'='*80}")
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"{'='*80}\n")
    
    return passed == len(results)

if __name__ == "__main__":
    print("\n🔧 Prerequisites:")
    print("   1. Backend server must be running on http://localhost:5000")
    print("   2. Database must be initialized")
    print("   3. A TelegramID with chat_id='2060245779' must exist in the database")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        exit(0)
    
    all_passed = run_all_tests()
    
    if all_passed:
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        exit(1)
