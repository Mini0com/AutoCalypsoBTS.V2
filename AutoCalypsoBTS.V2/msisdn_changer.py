#!/usr/bin/env python3
"""
OpenBSC MSISDN Changer Script
Connects to OpenBSC console via telnet and updates MSISDN in HLR database
"""

import telnetlib
import sqlite3
import sys
import time
import argparse
import re

class OpenBSCManager:
    def __init__(self, host='localhost', port=4242, hlr_path='/root/.osmocom/hlr.sqlite3'):
        self.host = host
        self.port = port
        self.hlr_path = hlr_path
        self.tn = None
        
    def connect_telnet(self):
        """Connect to OpenBSC telnet console"""
        try:
            self.tn = telnetlib.Telnet(self.host, self.port, timeout=10)
            
            # Wait for initial prompt
            time.sleep(1)
            
            # Send 'en' command to get full access
            self.tn.write(b"en\n")
            time.sleep(1)
            
            # Read response
            response = self.tn.read_very_eager().decode('utf-8')
            
            return True
            
        except Exception as e:
            return False
    
    def send_command(self, command):
        """Send command to OpenBSC console and return response"""
        if not self.tn:
            return None
            
        try:
            self.tn.write(f"{command}\n".encode('utf-8'))
            time.sleep(1)
            response = self.tn.read_very_eager().decode('utf-8')
            return response
        except Exception as e:
            return None
    
    def get_subscriber_info(self, subscriber_id):
        """Get subscriber information via console command"""
        command = f"show subscriber id {subscriber_id}"
        response = self.send_command(command)
        return response
    
    def update_msisdn_hlr(self, subscriber_id, new_msisdn):
        """Update MSISDN directly in HLR SQLite database"""
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(self.hlr_path)
            cursor = conn.cursor()
            
            # Check if subscriber exists by ID
            cursor.execute("SELECT id, imsi, msisdn FROM subscriber WHERE id = ?", (subscriber_id,))
            subscriber = cursor.fetchone()
            
            if not subscriber:
                conn.close()
                return False, "not_found"
            
            # Update MSISDN
            cursor.execute("UPDATE subscriber SET msisdn = ? WHERE id = ?", (new_msisdn, subscriber_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "success"
            else:
                conn.close()
                return False, "error"
                
        except sqlite3.Error as e:
            return False, "error"
        except Exception as e:
            return False, "error"
    
    def update_msisdn_console(self, subscriber_id, new_msisdn):
        """Update MSISDN/Extension via OpenBSC console commands"""
        try:
            # Use the correct OpenBSC console command format: subscriber id X extension Y
            command = f"subscriber id {subscriber_id} extension {new_msisdn}"
            response = self.send_command(command)
            
            # Check if subscriber not found
            if "not found" in response.lower() or "error" in response.lower():
                return False, "not_found"
            
            return "OK" in response or "Updated" in response or response.strip() != "", "success"
            
        except Exception as e:
            return False, "error"
    
    def sync_hlr(self):
        """Sync HLR database (if supported)"""
        response = self.send_command("subscriber sync")
    
    def disconnect(self):
        """Disconnect from telnet console"""
        if self.tn:
            try:
                self.tn.write(b"exit\n")
                self.tn.close()
            except:
                pass

def validate_subscriber_id(subscriber_id):
    """Validate subscriber ID format (should be a positive integer)"""
    try:
        return int(subscriber_id) > 0
    except ValueError:
        return False

def validate_msisdn(msisdn):
    """Validate MSISDN format (should be alphanumeric plus * and #, 4-15 characters)"""
    return re.match(r'^[a-zA-Z0-9*#]{4,15}$', msisdn) is not None

def main():
    parser = argparse.ArgumentParser(description='Update MSISDN in OpenBSC HLR')
    parser.add_argument('subscriber_id', help='Subscriber ID (positive integer)')
    parser.add_argument('extension', help='New extension/MSISDN (4-15 characters, alphanumeric plus * and #)')
    parser.add_argument('--host', default='localhost', help='OpenBSC console host (default: localhost)')
    parser.add_argument('--port', type=int, default=4242, help='OpenBSC console port (default: 4242)')
    parser.add_argument('--hlr-path', default='/root/.osmocom/hlr.sqlite3', 
                       help='Path to HLR SQLite database (default: /root/.osmocom/hlr.sqlite3)')
    parser.add_argument('--console-only', action='store_true', 
                       help='Only use console commands, skip direct database update')
    parser.add_argument('--db-only', action='store_true', 
                       help='Only update database directly, skip console commands')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not validate_subscriber_id(args.subscriber_id):
        print("Error: Subscriber ID must be a positive integer")
        sys.exit(1)
    
    if not validate_msisdn(args.extension):
        print("Error: Extension must be 4-15 characters, alphanumeric plus * and #")
        sys.exit(1)
    
    # Convert subscriber_id to integer
    subscriber_id = int(args.subscriber_id)
    
    # Create manager instance
    manager = OpenBSCManager(args.host, args.port, args.hlr_path)
    
    try:
        success = False
        not_found = False
        
        if not args.db_only:
            # Connect to telnet console
            if manager.connect_telnet():
                # Try to update via console
                result, status = manager.update_msisdn_console(subscriber_id, args.extension)
                if status == "not_found":
                    not_found = True
                elif result:
                    success = True
        
        if not args.console_only and not success and not not_found:
            # Update database directly
            result, status = manager.update_msisdn_hlr(subscriber_id, args.extension)
            if status == "not_found":
                not_found = True
            elif result:
                success = True
        
        if success:
            manager.sync_hlr()
        
        # Output only the required messages
        if success:
            print(f"Successfully updated MSISDN for Subscriber ID {subscriber_id}")
        elif not_found:
            print(f"No Subscriber found for id {subscriber_id}")
        else:
            print(f"Failed to update MSISDN for Subscriber ID {subscriber_id}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        manager.disconnect()

if __name__ == "__main__":
    main()
