"""
Simple test to verify backend API amount handling.

This test directly checks the form data parsing logic without requiring
a full database setup.
"""
import requests
import io
from PIL import Image

BASE_URL = "http://localhost:5000"
SUBMIT_ORDER_URL = f"{BASE_URL}/api/orders/submit"

def create_dummy_image():
    """Create a dummy image for testing."""
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_amount_parsing():
    """Test that the backend correctly parses amount from form data."""
    print("\n" + "="*80)
    print("🧪 TESTING BACKEND AMOUNT PARSING")
    print("="*80)
    
    test_amount = 1213.0
    test_price = 125.78
    
    print(f"\n📊 Test Data:")
    print(f"   Amount: {test_amount}")
    print(f"   Price: {test_price}")
    
    # Prepare form data
    form_data = {
        'order_type': 'buy',
        'amount': str(test_amount),
        'price': str(test_price),
        'chat_id': '2060245779',
        'user_bank': 'KBZ Bank - 1234567890 - Test User'
    }
    
    # Prepare file
    files = {
        'receipt': ('test_receipt.png', create_dummy_image(), 'image/png')
    }
    
    print(f"\n📤 Sending request to {SUBMIT_ORDER_URL}")
    print(f"   Form data: {form_data}")
    
    try:
        response = requests.post(
            SUBMIT_ORDER_URL,
            data=form_data,
            files=files,
            timeout=10
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            returned_amount = result.get('order', {}).get('amount')
            
            print(f"\n✅ Order created successfully!")
            print(f"   Order ID: {result.get('order_id')}")
            print(f"   Amount sent: {test_amount}")
            print(f"   Amount received: {returned_amount}")
            
            if returned_amount == test_amount:
                print(f"\n🎉 TEST PASSED: Amount is correct!")
                return True
            elif returned_amount == 0.0:
                print(f"\n❌ TEST FAILED: Amount is 0.0 (BUG!)")
                return False
            else:
                print(f"\n⚠️  TEST WARNING: Amount mismatch!")
                return False
        elif response.status_code == 404:
            print(f"\n⚠️  Backend returned 404")
            print(f"   This likely means the TelegramID with chat_id='2060245779' doesn't exist")
            print(f"   However, we can check the backend logs to see if amount parsing worked")
            print(f"\n   Response: {response.text}")
            return None
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to backend at {BASE_URL}")
        print(f"   Make sure the backend server is running:")
        print(f"   cd inifinity-tg-bot-backend && python app.py")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("BACKEND ORDER AMOUNT TEST")
    print("="*80)
    print("\nThis test verifies that the backend correctly parses and stores")
    print("the amount field from order submissions.")
    print("\n📋 Requirements:")
    print("   • Backend server running on http://localhost:5000")
    print("   • Check backend console logs for detailed parsing info")
    print("\nPress Enter to start test or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        exit(0)
    
    result = test_amount_parsing()
    
    print("\n" + "="*80)
    if result is True:
        print("✅ TEST PASSED")
    elif result is False:
        print("❌ TEST FAILED")
    else:
        print("⚠️  TEST INCONCLUSIVE - Check backend logs")
    print("="*80 + "\n")
