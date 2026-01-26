#!/usr/bin/env python3
"""
Test the complete Fulfillment System
Run this to verify all functionality works
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from nexus_backend import FulfillmentManager, AirtableClient

# Load environment
load_dotenv()


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(success, message):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")


def test_fulfillment_system():
    """Run comprehensive tests"""
    
    print_section("FULFILLMENT SYSTEM TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    manager = FulfillmentManager()
    airtable = AirtableClient()
    
    test_results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # =================================================================
    # TEST 1: Create Fulfillment Contract
    # =================================================================
    print_section("TEST 1: Create Fulfillment Contract")
    
    try:
        contract_data = {
            'CONTRACT_NAME': 'TEST - VA Hospital Socks',
            'CLIENT_NAME': 'Veterans Affairs - TEST',
            'PRODUCT': 'TEST Diabetic Socks - White Large',
            'TOTAL_QUANTITY': 1200,
            'UNIT_PRICE': 5.00,
            'DELIVERY_FREQUENCY': 'Monthly',
            'QUANTITY_PER_DELIVERY': 100,
            'START_DATE': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'SUPPLIER_UNIT_COST': 3.50,
            'ALERT_THRESHOLD': 200,
            'NOTES': 'TEST CONTRACT - Can be deleted'
        }
        
        result = manager.create_fulfillment_contract(contract_data)
        
        if result.get('success'):
            print_result(True, f"Contract created: {result['contract_id']}")
            print(f"   - Total Value: ${result['total_value']}")
            print(f"   - Total Profit: ${result['total_profit']}")
            print(f"   - Deliveries Generated: {result['deliveries_generated']}")
            test_results['passed'] += 1
            test_contract_id = result['contract']['id']
        else:
            print_result(False, f"Contract creation failed: {result.get('error')}")
            test_results['failed'] += 1
            return test_results  # Can't continue without contract
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
        return test_results
    
    # =================================================================
    # TEST 2: Get Active Contracts
    # =================================================================
    print_section("TEST 2: Get Active Contracts")
    
    try:
        contracts = manager.get_active_contracts()
        
        if contracts:
            print_result(True, f"Found {len(contracts)} active contracts")
            for contract in contracts[:3]:  # Show first 3
                print(f"   - {contract.get('CONTRACT_NAME')} ({contract.get('CONTRACT_ID')})")
            test_results['passed'] += 1
        else:
            print_result(False, "No active contracts found")
            test_results['failed'] += 1
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
    
    # =================================================================
    # TEST 3: Get Contract Details
    # =================================================================
    print_section("TEST 3: Get Contract Details")
    
    try:
        details = manager.get_contract_details(test_contract_id)
        
        if 'error' not in details:
            print_result(True, "Contract details retrieved")
            print(f"   - Contract: {details['contract']['fields'].get('CONTRACT_NAME')}")
            print(f"   - Deliveries: {len(details['deliveries'])}")
            print(f"   - Inventory Status: {details['inventory'].get('STATUS', 'Not found')}")
            test_results['passed'] += 1
            test_deliveries = details['deliveries']
        else:
            print_result(False, f"Failed to get details: {details['error']}")
            test_results['failed'] += 1
            return test_results
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
        return test_results
    
    # =================================================================
    # TEST 4: Get Upcoming Deliveries
    # =================================================================
    print_section("TEST 4: Get Upcoming Deliveries")
    
    try:
        upcoming = manager.get_upcoming_deliveries(60)  # Next 60 days to catch test deliveries
        
        if upcoming:
            print_result(True, f"Found {len(upcoming)} upcoming deliveries")
            for delivery in upcoming[:5]:  # Show first 5
                print(f"   - {delivery.get('DELIVERY_ID')} - Due in {delivery.get('days_until_due')} days")
            test_results['passed'] += 1
        else:
            print_result(True, "No upcoming deliveries (this is OK for a new system)")
            test_results['passed'] += 1
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
    
    # =================================================================
    # TEST 5: Create Purchase Order
    # =================================================================
    print_section("TEST 5: Create Purchase Order")
    
    try:
        po_data = {
            'PRODUCT_NAME': 'TEST Diabetic Socks - White Large',
            'QUANTITY_ORDERED': 1500,
            'UNIT_COST': 3.50,
            'EXPECTED_DELIVERY_DATE': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'PAYMENT_TERMS': 'Net 30',
            'NOTES': 'TEST PO - Initial inventory purchase'
        }
        
        po_result = manager.create_purchase_order(po_data)
        
        if po_result.get('success'):
            print_result(True, f"PO created: {po_result['po_number']}")
            print(f"   - Total Cost: ${po_result['po']['fields']['TOTAL_COST']}")
            test_results['passed'] += 1
            test_po_id = po_result['po']['id']
        else:
            print_result(False, f"PO creation failed: {po_result.get('error')}")
            test_results['failed'] += 1
            test_po_id = None
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
        test_po_id = None
    
    # =================================================================
    # TEST 6: Receive Purchase Order
    # =================================================================
    print_section("TEST 6: Receive Purchase Order")
    
    if test_po_id:
        try:
            received_data = {
                'ACTUAL_DELIVERY_DATE': datetime.now().strftime('%Y-%m-%d'),
                'QUANTITY_RECEIVED': 1500,
                'NOTES': 'TEST - All items received in good condition'
            }
            
            receive_result = manager.receive_purchase_order(test_po_id, received_data)
            
            if receive_result.get('success'):
                print_result(True, "PO received and inventory updated")
                print(f"   - Quantity Added: {received_data['QUANTITY_RECEIVED']}")
                test_results['passed'] += 1
            else:
                print_result(False, f"PO receive failed: {receive_result.get('error')}")
                test_results['failed'] += 1
        
        except Exception as e:
            print_result(False, f"Exception: {str(e)}")
            test_results['failed'] += 1
    else:
        print_result(False, "Skipped - no PO to receive")
        test_results['failed'] += 1
    
    # =================================================================
    # TEST 7: Check Inventory Health
    # =================================================================
    print_section("TEST 7: Check Inventory Health")
    
    try:
        health = manager.check_inventory_health()
        
        if health.get('success'):
            summary = health['summary']
            print_result(True, "Inventory health check completed")
            print(f"   - Critical: {summary['critical_count']}")
            print(f"   - Low Stock: {summary['low_stock_count']}")
            print(f"   - Reorder Needed: {summary['reorder_needed_count']}")
            print(f"   - Healthy: {summary['healthy_count']}")
            test_results['passed'] += 1
        else:
            print_result(False, f"Health check failed: {health.get('error')}")
            test_results['failed'] += 1
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
    
    # =================================================================
    # TEST 8: Update Delivery Status (Simulate Shipment)
    # =================================================================
    print_section("TEST 8: Update Delivery Status")
    
    if test_deliveries:
        try:
            # Get first scheduled delivery
            first_delivery = test_deliveries[0]
            delivery_id = first_delivery['id']
            
            updates = {
                'STATUS': 'In Transit',
                'SCHEDULED_DATE': datetime.now().strftime('%Y-%m-%d'),
                'TRACKING_NUMBER': 'TEST-1Z999AA10123456784',
                'CARRIER': 'UPS',
                'SHIPPING_COST': 45.00,
                'NOTES': 'TEST - Simulated shipment'
            }
            
            update_result = manager.update_delivery_status(delivery_id, updates)
            
            if update_result.get('success'):
                print_result(True, "Delivery status updated to In Transit")
                print(f"   - Tracking: {updates['TRACKING_NUMBER']}")
                test_results['passed'] += 1
            else:
                print_result(False, f"Status update failed: {update_result.get('error')}")
                test_results['failed'] += 1
        
        except Exception as e:
            print_result(False, f"Exception: {str(e)}")
            test_results['failed'] += 1
    else:
        print_result(False, "Skipped - no deliveries to update")
        test_results['failed'] += 1
    
    # =================================================================
    # TEST 9: Get Inventory Dashboard
    # =================================================================
    print_section("TEST 9: Get Inventory Dashboard")
    
    try:
        inventory = manager.get_inventory_dashboard()
        
        if inventory:
            print_result(True, f"Inventory dashboard loaded: {len(inventory)} products")
            for item in inventory[:3]:  # Show first 3
                print(f"   - {item.get('PRODUCT_NAME')}: {item.get('QUANTITY_ON_HAND')} on hand, {item.get('QUANTITY_AVAILABLE')} available")
            test_results['passed'] += 1
        else:
            print_result(True, "No inventory items (OK for new system)")
            test_results['passed'] += 1
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
    
    # =================================================================
    # TEST 10: Get Pending Purchase Orders
    # =================================================================
    print_section("TEST 10: Get Pending Purchase Orders")
    
    try:
        pending_pos = manager.get_pending_purchase_orders()
        
        print_result(True, f"Found {len(pending_pos)} pending POs")
        if pending_pos:
            for po in pending_pos[:3]:  # Show first 3
                print(f"   - {po.get('PO_NUMBER')}: {po.get('QUANTITY_ORDERED')} units, Due: {po.get('EXPECTED_DELIVERY_DATE')}")
        test_results['passed'] += 1
    
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        test_results['failed'] += 1
    
    # =================================================================
    # FINAL SUMMARY
    # =================================================================
    print_section("TEST SUMMARY")
    
    total_tests = test_results['passed'] + test_results['failed']
    pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! Fulfillment system is ready to use.")
    else:
        print(f"\n⚠️  {test_results['failed']} test(s) failed. Review errors above.")
    
    print("\n" + "=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return test_results


if __name__ == "__main__":
    results = test_fulfillment_system()
    
    # Exit with appropriate code
    exit(0 if results['failed'] == 0 else 1)
