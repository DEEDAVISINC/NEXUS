#!/usr/bin/env python3
"""
Fulfillment System Automated Monitor
Run this daily (cron job) to check inventory and send alerts
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from nexus_backend import FulfillmentManager, AirtableClient

# Load environment
load_dotenv()


class FulfillmentMonitor:
    """Automated monitoring and alerting for fulfillment system"""
    
    def __init__(self):
        self.manager = FulfillmentManager()
        self.airtable = AirtableClient()
    
    def run_daily_checks(self):
        """Run all daily checks and generate alerts"""
        print("=" * 60)
        print(f"FULFILLMENT SYSTEM DAILY CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        alerts = {
            'critical': [],
            'warnings': [],
            'info': []
        }
        
        # 1. Check inventory health
        print("\n📦 Checking inventory health...")
        inventory_alerts = self._check_inventory()
        alerts['critical'].extend(inventory_alerts['critical'])
        alerts['warnings'].extend(inventory_alerts['warnings'])
        alerts['info'].extend(inventory_alerts['info'])
        
        # 2. Check upcoming deliveries
        print("\n🚚 Checking upcoming deliveries...")
        delivery_alerts = self._check_deliveries()
        alerts['critical'].extend(delivery_alerts['critical'])
        alerts['warnings'].extend(delivery_alerts['warnings'])
        alerts['info'].extend(delivery_alerts['info'])
        
        # 3. Check overdue deliveries
        print("\n⏰ Checking for overdue deliveries...")
        overdue_alerts = self._check_overdue_deliveries()
        alerts['critical'].extend(overdue_alerts)
        
        # 4. Check pending POs
        print("\n📋 Checking pending purchase orders...")
        po_alerts = self._check_purchase_orders()
        alerts['warnings'].extend(po_alerts)
        
        # 5. Generate summary report
        print("\n📊 Generating summary report...")
        self._print_summary(alerts)
        
        # 6. Send alerts (if configured)
        if os.environ.get('SEND_ALERTS') == 'true':
            self._send_alerts(alerts)
        
        print("\n✅ Daily check complete!")
        return alerts
    
    def _check_inventory(self):
        """Check inventory health and return alerts"""
        alerts = {
            'critical': [],
            'warnings': [],
            'info': []
        }
        
        health_check = self.manager.check_inventory_health()
        
        if not health_check.get('success'):
            alerts['critical'].append(f"❌ Inventory check failed: {health_check.get('error')}")
            return alerts
        
        inventory_alerts = health_check.get('alerts', {})
        
        # Critical: Cannot fulfill commitments
        for item in inventory_alerts.get('critical', []):
            msg = f"🚨 CRITICAL: {item['product']} - {item['alert']} - ACTION: {item['action']}"
            alerts['critical'].append(msg)
            print(f"  {msg}")
        
        # Warnings: Low stock
        for item in inventory_alerts.get('low_stock', []):
            msg = f"⚠️  WARNING: {item['product']} - {item['alert']} - ACTION: {item['action']}"
            alerts['warnings'].append(msg)
            print(f"  {msg}")
        
        # Reorder needed
        for item in inventory_alerts.get('reorder_needed', []):
            msg = f"⚠️  REORDER: {item['product']} - {item['alert']} - ACTION: {item['action']}"
            alerts['warnings'].append(msg)
            print(f"  {msg}")
        
        # Info: Healthy items
        healthy_count = len(inventory_alerts.get('healthy', []))
        if healthy_count > 0:
            msg = f"✅ {healthy_count} products have healthy inventory levels"
            alerts['info'].append(msg)
            print(f"  {msg}")
        
        return alerts
    
    def _check_deliveries(self):
        """Check deliveries due in next 7 days"""
        alerts = {
            'critical': [],
            'warnings': [],
            'info': []
        }
        
        # Check deliveries due in next 7 days
        upcoming = self.manager.get_upcoming_deliveries(7)
        
        if not upcoming:
            alerts['info'].append("ℹ️  No deliveries due in next 7 days")
            print("  ℹ️  No deliveries due in next 7 days")
            return alerts
        
        # Group by urgency
        critical_deliveries = [d for d in upcoming if d['days_until_due'] <= 2]
        warning_deliveries = [d for d in upcoming if 3 <= d['days_until_due'] <= 5]
        info_deliveries = [d for d in upcoming if d['days_until_due'] > 5]
        
        # Critical: Due in 0-2 days
        for delivery in critical_deliveries:
            days = delivery['days_until_due']
            day_text = "TODAY" if days == 0 else f"{days} days"
            msg = f"🚨 URGENT: Delivery {delivery.get('DELIVERY_ID')} due in {day_text} - {delivery.get('QUANTITY')} units"
            alerts['critical'].append(msg)
            print(f"  {msg}")
            
            # Check if inventory is sufficient
            product = self._get_product_from_delivery(delivery)
            if product:
                inventory = self.manager._get_inventory_status(product)
                available = inventory.get('QUANTITY_AVAILABLE', 0)
                needed = delivery.get('QUANTITY', 0)
                
                if available < needed:
                    shortage_msg = f"  ❌ INVENTORY SHORT: Need {needed}, only {available} available!"
                    alerts['critical'].append(shortage_msg)
                    print(f"  {shortage_msg}")
        
        # Warnings: Due in 3-5 days
        for delivery in warning_deliveries:
            days = delivery['days_until_due']
            msg = f"⚠️  UPCOMING: Delivery {delivery.get('DELIVERY_ID')} due in {days} days - {delivery.get('QUANTITY')} units"
            alerts['warnings'].append(msg)
            print(f"  {msg}")
        
        # Info: Due in 6-7 days
        if info_deliveries:
            msg = f"ℹ️  {len(info_deliveries)} deliveries scheduled in 6-7 days"
            alerts['info'].append(msg)
            print(f"  {msg}")
        
        return alerts
    
    def _check_overdue_deliveries(self):
        """Check for deliveries past their due date"""
        alerts = []
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Find deliveries that are past due and not delivered
            formula = f"AND({{DUE_DATE}} < '{today}', {{STATUS}} != 'Delivered', {{STATUS}} != 'Cancelled')"
            overdue = self.airtable.search_records('FULFILLMENT DELIVERIES', formula)
            
            if not overdue:
                print("  ✅ No overdue deliveries")
                return alerts
            
            for delivery in overdue:
                fields = delivery['fields']
                due_date = datetime.strptime(fields['DUE_DATE'], '%Y-%m-%d')
                days_late = (datetime.now() - due_date).days
                
                msg = f"🚨 LATE: Delivery {fields.get('DELIVERY_ID')} is {days_late} days overdue - Status: {fields.get('STATUS')}"
                alerts.append(msg)
                print(f"  {msg}")
        
        except Exception as e:
            print(f"  ❌ Error checking overdue deliveries: {e}")
        
        return alerts
    
    def _check_purchase_orders(self):
        """Check pending purchase orders"""
        alerts = []
        
        pending_pos = self.manager.get_pending_purchase_orders()
        
        if not pending_pos:
            print("  ℹ️  No pending purchase orders")
            return alerts
        
        today = datetime.now()
        
        for po in pending_pos:
            expected_date_str = po.get('EXPECTED_DELIVERY_DATE')
            if not expected_date_str:
                continue
            
            expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d')
            days_until = (expected_date - today).days
            
            if days_until < 0:
                msg = f"⚠️  PO {po.get('PO_NUMBER')} is {abs(days_until)} days overdue"
                alerts.append(msg)
                print(f"  {msg}")
            elif days_until <= 3:
                msg = f"ℹ️  PO {po.get('PO_NUMBER')} expected in {days_until} days - {po.get('QUANTITY_ORDERED')} units"
                alerts.append(msg)
                print(f"  {msg}")
        
        return alerts
    
    def _get_product_from_delivery(self, delivery):
        """Get product name from delivery's contract"""
        try:
            contract_ids = delivery.get('CONTRACT', [])
            if contract_ids:
                contract = self.airtable.get_record('FULFILLMENT CONTRACTS', contract_ids[0])
                return contract['fields'].get('PRODUCT', '')
        except:
            pass
        return None
    
    def _print_summary(self, alerts):
        """Print summary of alerts"""
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"🚨 Critical Alerts: {len(alerts['critical'])}")
        print(f"⚠️  Warnings: {len(alerts['warnings'])}")
        print(f"ℹ️  Info: {len(alerts['info'])}")
        
        if alerts['critical']:
            print("\n🚨 CRITICAL ACTIONS NEEDED:")
            for alert in alerts['critical']:
                print(f"  - {alert}")
        
        if not alerts['critical'] and not alerts['warnings']:
            print("\n✅ All systems healthy!")
    
    def _send_alerts(self, alerts):
        """Send alerts via email/SMS (implement based on your needs)"""
        # TODO: Integrate with email service (SendGrid, SES, etc.)
        # TODO: Integrate with SMS service (Twilio, etc.)
        print("\n📧 Alert sending is configured but not yet implemented")
        print("   Implement email/SMS integration in _send_alerts() method")


def main():
    """Run the daily check"""
    monitor = FulfillmentMonitor()
    alerts = monitor.run_daily_checks()
    
    # Return exit code based on alerts
    if alerts['critical']:
        exit(1)  # Critical issues found
    else:
        exit(0)  # All good


if __name__ == "__main__":
    main()
