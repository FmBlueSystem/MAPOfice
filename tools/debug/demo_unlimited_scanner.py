#!/usr/bin/env python3
"""
Demo Script for Unlimited Library Scanner
=========================================

This script demonstrates the PersistentLibraryScanner functionality with a real
music library. It shows:

1. Unlimited recursive scanning
2. Progress reporting 
3. Database persistence
4. Cache efficiency
5. Memory usage monitoring

Usage:
    python demo_unlimited_scanner.py /path/to/music/library

Example:
    python demo_unlimited_scanner.py ~/Music
"""

import sys
import os
import time
from pathlib import Path

# Add project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtCore import QCoreApplication
from src.services.persistent_library_scanner import PersistentLibraryScanner, ScanProgress


class ScannerDemo:
    """Demo class for unlimited scanner"""
    
    def __init__(self, library_path: str):
        self.library_path = library_path
        self.scanner = None
        self.start_time = 0
        
    def setup_scanner(self):
        """Initialize scanner with default database"""
        print("🔧 Initializing Unlimited Library Scanner...")
        self.scanner = PersistentLibraryScanner()
        
        # Connect progress signals
        self.scanner.scan_progress.connect(self.on_progress_update)
        self.scanner.scan_completed.connect(self.on_scan_completed)
        self.scanner.scan_error.connect(self.on_scan_error)
        
        print("✅ Scanner initialized successfully")
        
    def on_progress_update(self, progress: ScanProgress):
        """Handle progress updates"""
        elapsed = time.time() - self.start_time
        
        print(f"\r⏱️  Progress: {progress.files_processed}/{progress.files_discovered} files "
              f"({progress.cache_hit_rate:.1%} cached) "
              f"| Speed: {progress.scan_speed:.1f} files/sec "
              f"| Memory: {progress.memory_usage_mb:.1f}MB "
              f"| Elapsed: {elapsed:.1f}s", end="", flush=True)
              
    def on_scan_completed(self, final_stats: dict):
        """Handle scan completion"""
        print(f"\n\n🎉 Scan completed successfully!")
        print(f"📊 Final Statistics:")
        print(f"   Files discovered: {final_stats.get('files_discovered', 0)}")
        print(f"   Files analyzed: {final_stats.get('files_analyzed', 0)}")
        print(f"   Files cached: {final_stats.get('files_cached', 0)}")
        print(f"   Files skipped: {final_stats.get('files_skipped', 0)}")
        print(f"   Files with errors: {final_stats.get('files_error', 0)}")
        print(f"   Cache hit rate: {final_stats.get('cache_hit_rate', 0):.1%}")
        print(f"   Scan speed: {final_stats.get('scan_speed', 0):.1f} files/sec")
        print(f"   Total duration: {final_stats.get('scan_duration', 0):.1f} seconds")
        
        # Show database statistics
        print(f"\n📚 Database Statistics:")
        db_stats = self.scanner.get_library_statistics()
        print(f"   Total tracks: {db_stats.get('total_tracks', 0)}")
        print(f"   Tracks with BPM: {db_stats.get('tracks_with_bpm', 0)}")
        print(f"   Complete tracks: {db_stats.get('complete_tracks', 0)}")
        
        if 'genre_distribution' in db_stats:
            print(f"   Top genres: {list(db_stats['genre_distribution'].items())[:5]}")
            
        if 'bpm_stats' in db_stats:
            bmp_stats = db_stats['bmp_stats']
            print(f"   BPM range: {bmp_stats.get('minimum', 0):.1f} - {bmp_stats.get('maximum', 0):.1f}")
            print(f"   Average BPM: {bmp_stats.get('average', 0):.1f}")
            
    def on_scan_error(self, error_message: str):
        """Handle scan errors"""
        print(f"\n❌ Scan error: {error_message}")
        
    def run_demo(self):
        """Run the unlimited scanner demo"""
        print("🚀 Unlimited Library Scanner Demo")
        print("=" * 50)
        
        # Setup scanner
        self.setup_scanner()
        
        # Validate library path
        try:
            print(f"📁 Validating library path: {self.library_path}")
            self.scanner.validate_library_path(self.library_path)
            print("✅ Library path is valid")
        except Exception as e:
            print(f"❌ Invalid library path: {e}")
            return False
            
        # Show initial database stats
        initial_stats = self.scanner.get_library_statistics()
        print(f"\n📊 Initial database state:")
        print(f"   Existing tracks: {initial_stats.get('total_tracks', 0)}")
        
        # Start unlimited scan
        print(f"\n🔍 Starting unlimited scan of: {self.library_path}")
        print("   Scan mode: smart (uses caching for efficiency)")
        print("   Press Ctrl+C to cancel scan\n")
        
        self.start_time = time.time()
        
        try:
            if self.scanner.start_unlimited_scan(self.library_path, scan_mode="smart"):
                print("✅ Scan started successfully")
                
                # Wait for completion (non-blocking)
                while self.scanner.is_scan_active():
                    QCoreApplication.processEvents()
                    time.sleep(0.1)
                    
            else:
                print("❌ Failed to start scan")
                return False
                
        except KeyboardInterrupt:
            print(f"\n🛑 Scan cancelled by user")
            self.scanner.cancel_scan()
            return False
            
        return True


def main():
    """Main demo execution"""
    if len(sys.argv) != 2:
        print("Usage: python demo_unlimited_scanner.py <library_path>")
        print("Example: python demo_unlimited_scanner.py ~/Music")
        return 1
        
    library_path = sys.argv[1]
    
    # Expand user path
    library_path = os.path.expanduser(library_path)
    
    if not os.path.exists(library_path):
        print(f"❌ Library path does not exist: {library_path}")
        return 1
        
    # Initialize Qt application for signals/slots
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
        
    try:
        # Create and run demo
        demo = ScannerDemo(library_path)
        success = demo.run_demo()
        
        if success:
            print("\n🎉 Demo completed successfully!")
            print("\n💡 The scanner has now indexed your music library.")
            print("   Subsequent scans will be much faster due to intelligent caching.")
            print("   Only new or modified files will be re-analyzed.")
            return 0
        else:
            print("\n⚠️  Demo completed with errors.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        return 1
        

if __name__ == "__main__":
    sys.exit(main())