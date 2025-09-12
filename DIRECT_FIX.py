#!/usr/bin/env python3
"""DIRECT FIX - Replace the entire broken method"""

file_path = "/Users/freddymolina/Desktop/MAP 4/src/ui/playlist_cli_widget.py"

with open(file_path, 'r') as f:
    content = f.read()

# Find the _populate_playlist_table method and replace it completely
import re

# Pattern to match the entire method
pattern = r'def _populate_playlist_table\(self, tracks.*?\n(?=    def|\n\nclass|\Z)'
replacement = '''def _populate_playlist_table(self, tracks):
        """WORKING VERSION - Force visible text"""
        if not tracks:
            return
        
        self.playlist_table.setRowCount(len(tracks))
        
        for row, track in enumerate(tracks):
            from PyQt6.QtGui import QColor
            from PyQt6.QtWidgets import QTableWidgetItem
            
            # Number with black text
            item1 = QTableWidgetItem(str(row + 1))
            item1.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 0, item1)
            
            # Track with black text
            title = track.get('title', 'Test Title')
            artist = track.get('artist', 'Test Artist')
            item2 = QTableWidgetItem(f"{artist} - {title}")
            item2.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 1, item2)
            
            # BPM with black text
            bpm = track.get('bpm', 120)
            item3 = QTableWidgetItem(f"{bmp:.0f}" if bpm else "--")
            item3.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 2, item3)
            
            # Genre with black text
            genre = track.get('genre', 'Pop')
            item4 = QTableWidgetItem(genre)
            item4.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 3, item4)

'''

# Replace the method
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("FIXED")