#!/usr/bin/env python3
"""
ATLAS PM Data Migration Utility

Migrates data from ATLAS PM HTML localStorage to NEXUS Airtable backend.
This utility helps transition from the standalone HTML system to the integrated NEXUS platform.

Usage:
    python atlas_migration.py --export-html-data <html_file>
    python atlas_migration.py --migrate-to-airtable <json_file>
    python atlas_migration.py --validate-migration
"""

import json
import re
import argparse
from datetime import datetime
from typing import Dict, List, Any
from pyairtable import Api


class ATLASMigration:
    """Handles migration of ATLAS PM data from HTML localStorage to Airtable"""

    def __init__(self, airtable_api_key: str = None, airtable_base_id: str = None):
        self.airtable_api_key = airtable_api_key
        self.airtable_base_id = airtable_base_id
        if airtable_api_key and airtable_base_id:
            self.airtable = Api(airtable_api_key).table(airtable_base_id, '')
        else:
            self.airtable = None

    def extract_data_from_html(self, html_file_path: str) -> Dict[str, Any]:
        """
        Extract ATLAS PM data from HTML file localStorage initialization

        Returns data structure compatible with ATLAS PM localStorage format
        """
        print(f"Extracting data from {html_file_path}...")

        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract localStorage data patterns
        data_patterns = {
            'activeProjects': r'const \[activeProjects, setActiveProjects\] = useState\((.*?)\);',
            'activeRFPs': r'const \[activeRFPs, setActiveRFPs\] = useState\((.*?)\);',
            'changeOrders': r'const \[changeOrders, setChangeOrders\] = useState\((.*?)\);',
            'projectLogs': r'const \[projectLogs, setProjectLogs\] = useState\((.*?)\);'
        }

        extracted_data = {}

        for key, pattern in data_patterns.items():
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                data_str = match.group(1)
                try:
                    # Clean up the JavaScript array/object syntax for JSON parsing
                    cleaned_data = self._clean_js_data(data_str)
                    extracted_data[key] = json.loads(cleaned_data)
                    print(f"✓ Extracted {key}: {len(extracted_data[key])} items")
                except json.JSONDecodeError as e:
                    print(f"✗ Failed to parse {key}: {e}")
                    extracted_data[key] = []
            else:
                print(f"✗ No data found for {key}")
                extracted_data[key] = []

        return extracted_data

    def _clean_js_data(self, js_data: str) -> str:
        """Clean JavaScript data syntax to make it JSON-compatible"""
        # Remove JavaScript-specific syntax
        cleaned = js_data.strip()

        # Handle empty arrays/objects
        if cleaned in ['[]', '{}']:
            return cleaned

        # Remove trailing commas
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)

        # Handle single quotes (convert to double quotes)
        cleaned = re.sub(r"'([^']*)'", r'"\1"', cleaned)

        return cleaned

    def transform_project_data(self, html_projects: List[Dict]) -> List[Dict]:
        """Transform HTML project data to Airtable format"""
        airtable_projects = []

        for project in html_projects:
            airtable_project = {
                'Project Name': project.get('name', ''),
                'Client Name': project.get('client', ''),
                'Project Type': project.get('type', 'Consulting'),
                'Industry': project.get('industry', ''),
                'Project Scope': project.get('scope', ''),
                'Budget': project.get('budget', 0),
                'Timeline': project.get('timeline', ''),
                'Status': project.get('status', 'Planning'),
                'Priority': project.get('priority', 'Medium'),
                'Completion Percentage': project.get('completion_percentage', 0),
                'Risk Level': project.get('risk_level', 'Medium'),
                'Created Date': datetime.now().isoformat()
            }
            airtable_projects.append(airtable_project)

        return airtable_projects

    def transform_rfp_data(self, html_rfps: List[Dict]) -> List[Dict]:
        """Transform HTML RFP data to Airtable format"""
        airtable_rfps = []

        for rfp in html_rfps:
            airtable_rfp = {
                'RFP Name': rfp.get('name', ''),
                'Client Name': rfp.get('client', ''),
                'RFP Number': rfp.get('rfpNumber', ''),
                'Value': rfp.get('value', 0),
                'Due Date': rfp.get('dueDate'),
                'Industry': rfp.get('industry', ''),
                'Description': rfp.get('description', ''),
                'Contact Name': rfp.get('contact', ''),
                'Status': rfp.get('status', 'Draft'),
                'Probability': rfp.get('probability', 50),
                'Created Date': datetime.now().isoformat()
            }
            airtable_rfps.append(airtable_rfp)

        return airtable_rfps

    def transform_change_order_data(self, html_change_orders: Dict[str, List]) -> List[Dict]:
        """Transform HTML change orders data to Airtable format"""
        airtable_cos = []

        for project_id, orders in html_change_orders.items():
            for order in orders:
                airtable_co = {
                    'Project ID': project_id,
                    'Title': order.get('title', ''),
                    'Description': order.get('description', ''),
                    'Type': order.get('type', 'Scope'),
                    'Priority': order.get('priority', 'Medium'),
                    'Status': order.get('status', 'Draft'),
                    'Impact Scope': order.get('impact_scope', 'Low'),
                    'Impact Schedule': order.get('impact_schedule', ''),
                    'Impact Budget': order.get('impact_budget', 0),
                    'Requested By': order.get('requested_by', ''),
                    'Created Date': order.get('created_date', datetime.now().isoformat())
                }
                airtable_cos.append(airtable_co)

        return airtable_cos

    def migrate_to_airtable(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate extracted data to Airtable"""
        if not self.airtable:
            raise ValueError("Airtable client not initialized")

        migration_results = {
            'projects': {'migrated': 0, 'errors': 0},
            'rfps': {'migrated': 0, 'errors': 0},
            'change_orders': {'migrated': 0, 'errors': 0}
        }

        print("Starting migration to Airtable...")

        # Migrate Projects
        if extracted_data.get('activeProjects'):
            projects_data = self.transform_project_data(extracted_data['activeProjects'])
            for project in projects_data:
                try:
                    self.airtable.create('ATLAS Projects', project)
                    migration_results['projects']['migrated'] += 1
                except Exception as e:
                    print(f"Error migrating project: {e}")
                    migration_results['projects']['errors'] += 1

        # Migrate RFPs
        if extracted_data.get('activeRFPs'):
            rfps_data = self.transform_rfp_data(extracted_data['activeRFPs'])
            for rfp in rfps_data:
                try:
                    self.airtable.create('ATLAS RFPs', rfp)
                    migration_results['rfps']['migrated'] += 1
                except Exception as e:
                    print(f"Error migrating RFP: {e}")
                    migration_results['rfps']['errors'] += 1

        # Migrate Change Orders
        if extracted_data.get('changeOrders'):
            cos_data = self.transform_change_order_data(extracted_data['changeOrders'])
            for co in cos_data:
                try:
                    self.airtable.create('ATLAS Change Orders', co)
                    migration_results['change_orders']['migrated'] += 1
                except Exception as e:
                    print(f"Error migrating change order: {e}")
                    migration_results['change_orders']['errors'] += 1

        print("Migration completed!")
        return migration_results

    def validate_migration(self) -> Dict[str, Any]:
        """Validate that migration was successful by checking Airtable data"""
        if not self.airtable:
            raise ValueError("Airtable client not initialized")

        validation_results = {}

        tables_to_check = ['ATLAS Projects', 'ATLAS RFPs', 'ATLAS Change Orders']

        for table_name in tables_to_check:
            try:
                records = self.airtable.all(table_name)
                validation_results[table_name] = {
                    'record_count': len(records),
                    'has_required_fields': self._validate_table_schema(records, table_name),
                    'sample_record': records[0]['fields'] if records else None
                }
            except Exception as e:
                validation_results[table_name] = {'error': str(e)}

        return validation_results

    def _validate_table_schema(self, records: List[Dict], table_name: str) -> bool:
        """Validate that records have expected schema"""
        if not records:
            return True  # Empty table is valid

        required_fields = {
            'ATLAS Projects': ['Project Name', 'Client Name', 'Status'],
            'ATLAS RFPs': ['RFP Name', 'Client Name', 'Status'],
            'ATLAS Change Orders': ['Title', 'Description', 'Status']
        }

        sample_record = records[0]['fields']
        expected_fields = required_fields.get(table_name, [])

        return all(field in sample_record for field in expected_fields)


def main():
    parser = argparse.ArgumentParser(description='ATLAS PM Data Migration Utility')
    parser.add_argument('--export-html-data', help='Extract data from ATLAS PM HTML file')
    parser.add_argument('--migrate-to-airtable', help='Migrate JSON data to Airtable')
    parser.add_argument('--validate-migration', action='store_true', help='Validate migration results')
    parser.add_argument('--airtable-key', help='Airtable API key')
    parser.add_argument('--airtable-base', help='Airtable base ID')

    args = parser.parse_args()

    # Initialize migration utility
    migrator = ATLASMigration(args.airtable_key, args.airtable_base)

    if args.export_html_data:
        # Extract data from HTML file
        data = migrator.extract_data_from_html(args.export_html_data)

        # Save to JSON file
        output_file = 'atlas_extracted_data.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Data extracted and saved to {output_file}")
        print(f"Summary: {len(data.get('activeProjects', []))} projects, {len(data.get('activeRFPs', []))} RFPs")

    elif args.migrate_to_airtable:
        # Load data from JSON file
        with open(args.migrate_to_airtable, 'r') as f:
            data = json.load(f)

        # Migrate to Airtable
        results = migrator.migrate_to_airtable(data)
        print("Migration Results:")
        print(json.dumps(results, indent=2))

    elif args.validate_migration:
        # Validate migration
        results = migrator.validate_migration()
        print("Validation Results:")
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
