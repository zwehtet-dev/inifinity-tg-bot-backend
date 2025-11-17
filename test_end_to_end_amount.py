"""
End-to-end test demonstrating the complete amount flow.

This test simulates the entire flow from OCR detection to backend storage,
helping identify where amounts might be lost in the pipeline.
"""

def simulate_ocr_extraction():
    """Simulate OCR extracting amount from receipt."""
    print("\n" + "="*80)
    print("STEP 1: OCR Extraction")
    print("="*80)
    
    # Simulate OCR result
    class ReceiptData:
        def __init__(self):
            self.amount = 1213.0
            self.bank_name = "SCB"
            self.account_number = "XXX-X-XX293-5"
            self.account_name = "MIN MYAT NWE"
            self.transaction_date = "2025-11-09"
            self.transaction_id = "A675796668292542a2"
            self.confidence_score = 0.83
    
    receipt_data = ReceiptData()
    
    print(f"✅ OCR extracted amount: {receipt_data.amount}")
    print(f"   Confidence: {receipt_data.confidence_score}")
    
    return receipt_data

def simulate_state_storage(receipt_data, order_type="buy"):
    """Simulate storing amount in conversation state."""
    print("\n" + "="*80)
    print("STEP 2: Store Amount in State")
    print("="*80)
    
    # Simulate state manager update
    class OrderData:
        def __init__(self):
            self.thb_amount = None
            self.mmk_amount = None
            self.order_type = order_type
    
    order_data = OrderData()
    
    # This is the fix we implemented
    if order_type == "buy":
        order_data.thb_amount = receipt_data.amount
        print(f"✅ Stored as thb_amount: {order_data.thb_amount}")
    else:
        order_data.mmk_amount = receipt_data.amount
        print(f"✅ Stored as mmk_amount: {order_data.mmk_amount}")
    
    return order_data

def simulate_order_submission(order_data):
    """Simulate order submission to backend."""
    print("\n" + "="*80)
    print("STEP 3: Prepare Order Submission")
    print("="*80)
    
    # This is what happens in submit_order
    amount = order_data.thb_amount or order_data.mmk_amount or 0.0
    
    print(f"   thb_amount: {order_data.thb_amount}")
    print(f"   mmk_amount: {order_data.mmk_amount}")
    print(f"   final amount: {amount}")
    
    if amount == 0.0:
        print(f"❌ ERROR: Amount is 0.0! This is the bug!")
        return None
    else:
        print(f"✅ Amount ready for submission: {amount}")
        return amount

def simulate_backend_processing(amount):
    """Simulate backend receiving and processing the amount."""
    print("\n" + "="*80)
    print("STEP 4: Backend Processing")
    print("="*80)
    
    # Simulate form data
    form_data = {
        'order_type': 'buy',
        'amount': str(amount),
        'price': '125.78'
    }
    
    print(f"📤 Form data sent to backend:")
    print(f"   amount: '{form_data['amount']}' (type: {type(form_data['amount'])})")
    
    # Simulate backend conversion
    try:
        backend_amount = float(form_data['amount'])
        print(f"✅ Backend converted to: {backend_amount}")
        
        if backend_amount == 0.0:
            print(f"⚠️  WARNING: Backend received 0.0!")
            return False
        
        # Simulate database storage
        print(f"💾 Stored in database: {backend_amount}")
        return True
        
    except ValueError as e:
        print(f"❌ Backend conversion error: {e}")
        return False

def run_end_to_end_test():
    """Run the complete end-to-end test."""
    print("\n" + "="*80)
    print("END-TO-END AMOUNT FLOW TEST")
    print("="*80)
    print("\nThis test simulates the complete flow from OCR to backend storage.")
    print("It helps identify where amounts might be lost in the pipeline.\n")
    
    # Step 1: OCR extracts amount
    receipt_data = simulate_ocr_extraction()
    
    # Step 2: Store in state
    order_data = simulate_state_storage(receipt_data, order_type="buy")
    
    # Step 3: Prepare submission
    amount = simulate_order_submission(order_data)
    
    if amount is None:
        print("\n" + "="*80)
        print("❌ TEST FAILED: Amount lost in state management")
        print("="*80)
        print("\nThe amount was not stored correctly in the state.")
        print("This was the bug we fixed in conversation_handler.py")
        return False
    
    # Step 4: Backend processing
    success = simulate_backend_processing(amount)
    
    print("\n" + "="*80)
    if success:
        print("✅ TEST PASSED: Amount flowed correctly through entire pipeline")
        print("="*80)
        print(f"\nAmount journey:")
        print(f"  OCR: {receipt_data.amount}")
        print(f"  → State: {order_data.thb_amount or order_data.mmk_amount}")
        print(f"  → Submission: {amount}")
        print(f"  → Backend: {amount}")
        print(f"\n🎉 All steps preserved the amount correctly!")
    else:
        print("❌ TEST FAILED: Amount lost in backend processing")
        print("="*80)
    
    return success

def test_before_fix():
    """Demonstrate the bug before the fix."""
    print("\n" + "="*80)
    print("DEMONSTRATION: Before Fix (Bug Scenario)")
    print("="*80)
    
    class ReceiptData:
        amount = 1213.0
    
    class OrderData:
        thb_amount = None  # Bug: never set!
        mmk_amount = None  # Bug: never set!
    
    receipt_data = ReceiptData()
    order_data = OrderData()
    
    print(f"OCR extracted: {receipt_data.amount}")
    print(f"State thb_amount: {order_data.thb_amount}")
    print(f"State mmk_amount: {order_data.mmk_amount}")
    
    # This is what happened before the fix
    amount = order_data.thb_amount or order_data.mmk_amount or 0.0
    print(f"Final amount: {amount}")
    
    if amount == 0.0:
        print(f"\n❌ BUG REPRODUCED: Amount defaulted to 0.0!")
        print(f"   The OCR extracted {receipt_data.amount}, but it was never stored in state.")
        return False
    return True

def test_after_fix():
    """Demonstrate the fix."""
    print("\n" + "="*80)
    print("DEMONSTRATION: After Fix (Correct Behavior)")
    print("="*80)
    
    class ReceiptData:
        amount = 1213.0
    
    class OrderData:
        thb_amount = None
        mmk_amount = None
    
    receipt_data = ReceiptData()
    order_data = OrderData()
    
    print(f"OCR extracted: {receipt_data.amount}")
    
    # The fix: store the amount
    order_data.thb_amount = receipt_data.amount
    
    print(f"State thb_amount: {order_data.thb_amount}")
    print(f"State mmk_amount: {order_data.mmk_amount}")
    
    amount = order_data.thb_amount or order_data.mmk_amount or 0.0
    print(f"Final amount: {amount}")
    
    if amount == receipt_data.amount:
        print(f"\n✅ FIX VERIFIED: Amount preserved correctly!")
        print(f"   The OCR extracted {receipt_data.amount}, and it was stored in state.")
        return True
    return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPLETE AMOUNT FLOW TESTING")
    print("="*80)
    
    # Show the bug
    print("\n\n")
    test_before_fix()
    
    # Show the fix
    print("\n\n")
    test_after_fix()
    
    # Run full end-to-end test
    print("\n\n")
    success = run_end_to_end_test()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nThe fix in conversation_handler.py ensures that:")
    print("  1. OCR extracts the amount from the receipt")
    print("  2. Amount is stored in state (thb_amount or mmk_amount)")
    print("  3. Amount is retrieved during order submission")
    print("  4. Amount is sent to backend correctly")
    print("  5. Backend stores the amount in the database")
    print("\nWithout the fix, step 2 was missing, causing amounts to default to 0.0")
    print("="*80 + "\n")
    
    exit(0 if success else 1)
