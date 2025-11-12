#!/usr/bin/env python3
"""
Simple script to check database tables and discovered URLs.
"""

import sqlite3

def main():
    # Connect to database
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    # Check if discovered_urls table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='discovered_urls'")
    table_exists = cursor.fetchone()
    print(f'discovered_urls table exists: {table_exists is not None}')

    if table_exists:
        # Count total discovered URLs
        cursor.execute('SELECT COUNT(*) FROM discovered_urls')
        total_count = cursor.fetchone()[0]
        print(f'Total discovered URLs: {total_count}')
        
        # Show sample records if any
        cursor.execute('SELECT session_id, url, status_code FROM discovered_urls LIMIT 5')
        samples = cursor.fetchall()
        if samples:
            print('Sample discovered URLs:')
            for session_id, url, status_code in samples:
                print(f'  - Session: {session_id}, URL: {url}, Status: {status_code}')
    else:
        print('discovered_urls table does not exist')

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('\nAvailable tables:')
    for table in tables:
        print(f'  - {table[0]}')

    conn.close()

if __name__ == '__main__':
    main()