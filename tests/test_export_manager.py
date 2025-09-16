"""
Test suite for the Professional Export System
"""

import unittest
import json
import csv
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Import the export manager
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.services.export_manager import ExportManager
from src.services.export_templates import ExportTemplates


class TestExportManager(unittest.TestCase):
    """Test cases for ExportManager"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test exports
        self.temp_dir = tempfile.mkdtemp()
        self.export_mgr = ExportManager(self.temp_dir)

        # Sample test data
        self.sample_tracks = [
            {
                'name': 'Test Track 1',
                'artist': 'Test Artist 1',
                'bpm': 128,
                'key': 'C',
                'energy': 0.8,
                'genre': 'House',
                'path': '/path/to/track1.mp3'
            },
            {
                'name': 'Test Track 2',
                'artist': 'Test Artist 2',
                'bpm': 140,
                'key': 'Am',
                'energy': 0.9,
                'genre': 'Techno',
                'path': '/path/to/track2.mp3'
            }
        ]

        self.sample_data = {
            'metadata': {
                'version': '2.0',
                'export_date': datetime.now().isoformat()
            },
            'tracks': self.sample_tracks
        }

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_export_to_json(self):
        """Test JSON export functionality"""
        # Export data
        file_path = self.export_mgr.export_to_json(self.sample_data)

        # Verify file exists
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(str(file_path).endswith('.json'))

        # Verify content
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data['metadata']['version'], '2.0')
        self.assertEqual(len(loaded_data['tracks']), 2)
        self.assertEqual(loaded_data['tracks'][0]['name'], 'Test Track 1')

    def test_export_to_csv(self):
        """Test CSV export functionality"""
        # Export data
        file_path = self.export_mgr.export_to_csv(self.sample_tracks)

        # Verify file exists
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(str(file_path).endswith('.csv'))

        # Verify content
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['name'], 'Test Track 1')
        self.assertEqual(rows[0]['bpm'], '128')
        self.assertEqual(rows[1]['artist'], 'Test Artist 2')

    def test_export_to_csv_with_custom_columns(self):
        """Test CSV export with custom column selection"""
        # Export only specific columns
        columns = ['name', 'artist', 'bpm']
        file_path = self.export_mgr.export_to_csv(
            self.sample_tracks,
            columns=columns
        )

        # Verify content
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

        self.assertEqual(headers, columns)

    def test_export_analysis_report_html(self):
        """Test HTML report generation"""
        # Export HTML report
        file_path = self.export_mgr.export_analysis_report(
            self.sample_tracks,
            title="Test Analysis Report",
            format="html"
        )

        # Verify file exists
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(str(file_path).endswith('.html'))

        # Verify content
        with open(file_path, 'r') as f:
            html_content = f.read()

        self.assertIn('Test Analysis Report', html_content)
        self.assertIn('Test Track 1', html_content)
        self.assertIn('Test Artist 1', html_content)
        self.assertIn('128', html_content)  # BPM

    def test_export_playlist_analysis(self):
        """Test playlist analysis export"""
        playlist_data = {
            'name': 'Test Playlist',
            'tracks': self.sample_tracks,
            'compatibility_matrix': {
                '0_1': {'score': 0.85}
            }
        }

        # Export playlist analysis
        file_path = self.export_mgr.export_playlist_analysis(
            playlist_data,
            format="html"
        )

        # Verify file exists
        self.assertTrue(os.path.exists(file_path))
        self.assertIn('playlist', str(file_path).lower())

        # Verify content
        with open(file_path, 'r') as f:
            html_content = f.read()

        self.assertIn('Test Playlist', html_content)
        self.assertIn('Test Track 1', html_content)

    def test_batch_export(self):
        """Test batch export functionality"""
        data_sets = [
            {'name': 'dataset1', 'data': self.sample_tracks[:1]},
            {'name': 'dataset2', 'data': self.sample_tracks[1:]}
        ]

        # Batch export
        results = self.export_mgr.batch_export(
            data_sets,
            formats=['json', 'csv']
        )

        # Verify results
        self.assertIn('json', results)
        self.assertIn('csv', results)
        self.assertEqual(len(results['json']), 2)
        self.assertEqual(len(results['csv']), 2)

        # Verify files exist
        for format_type, paths in results.items():
            for path in paths:
                self.assertTrue(os.path.exists(path))

    def test_flatten_dict(self):
        """Test dictionary flattening for CSV export"""
        nested_data = {
            'track': 'Test Track',
            'metadata': {
                'bpm': 128,
                'key': 'C',
                'analysis': {
                    'energy': 0.8,
                    'confidence': 0.95
                }
            }
        }

        flattened = self.export_mgr._flatten_dict(nested_data)

        # Verify flattening
        self.assertEqual(flattened['track'], 'Test Track')
        self.assertEqual(flattened['metadata_bpm'], 128)
        self.assertEqual(flattened['metadata_key'], 'C')
        self.assertEqual(flattened['metadata_analysis_energy'], 0.8)
        self.assertEqual(flattened['metadata_analysis_confidence'], 0.95)

    def test_custom_template_creation(self):
        """Test custom template creation"""
        template_content = "<html><body>Custom Template</body></html>"
        template_path = self.export_mgr.create_custom_template(
            "custom_test",
            template_content
        )

        # Verify template created
        self.assertTrue(os.path.exists(template_path))
        self.assertIn('custom_test', str(template_path))

        # Verify content
        with open(template_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, template_content)

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        # Test empty list
        with self.assertRaises(ValueError):
            self.export_mgr.export_to_csv([])

        # Test JSON with empty data
        empty_data = {'tracks': []}
        file_path = self.export_mgr.export_to_json(empty_data)
        self.assertTrue(os.path.exists(file_path))

    def test_special_characters_handling(self):
        """Test handling of special characters in data"""
        special_tracks = [{
            'name': 'Track with "quotes" & <html>',
            'artist': "Artist's Name",
            'bpm': 120,
            'key': 'C#',
            'path': '/path/with spaces/track.mp3'
        }]

        # Test HTML export
        file_path = self.export_mgr.export_analysis_report(
            special_tracks,
            format="html"
        )

        with open(file_path, 'r') as f:
            html_content = f.read()

        # Verify HTML escaping
        self.assertIn('&quot;quotes&quot;', html_content)
        self.assertIn('&lt;html&gt;', html_content)

        # Test CSV export
        csv_path = self.export_mgr.export_to_csv(special_tracks)
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        self.assertEqual(row['name'], 'Track with "quotes" & <html>')


class TestExportTemplates(unittest.TestCase):
    """Test cases for ExportTemplates"""

    def setUp(self):
        """Set up test environment"""
        self.templates = ExportTemplates()
        self.sample_tracks = [
            {
                'name': 'Opening Track',
                'artist': 'DJ Test',
                'bpm': 124,
                'key': 'Am',
                'duration': 300
            },
            {
                'name': 'Peak Time',
                'artist': 'Producer X',
                'bpm': 128,
                'key': 'C',
                'duration': 360
            }
        ]

    def test_dj_setlist_template(self):
        """Test DJ setlist template generation"""
        event_info = {
            'name': 'Summer Festival 2024',
            'venue': 'Beach Club',
            'date': '2024-07-15'
        }

        html = self.templates.dj_setlist_template(
            self.sample_tracks,
            event_info
        )

        # Verify content
        self.assertIn('Summer Festival 2024', html)
        self.assertIn('Beach Club', html)
        self.assertIn('Opening Track', html)
        self.assertIn('124 BPM', html)

    def test_radio_show_template(self):
        """Test radio show template generation"""
        segments = [
            {
                'name': 'Opening Segment',
                'start_time': '00:00',
                'end_time': '15:00',
                'tracks': self.sample_tracks[:1]
            },
            {
                'name': 'Main Mix',
                'start_time': '15:00',
                'end_time': '30:00',
                'tracks': self.sample_tracks[1:]
            }
        ]

        show_info = {
            'name': 'Electronic Vibes',
            'host': 'DJ Test',
            'episode': '042'
        }

        html = self.templates.radio_show_template(segments, show_info)

        # Verify content
        self.assertIn('Electronic Vibes', html)
        self.assertIn('DJ Test', html)
        self.assertIn('Episode 042', html)
        self.assertIn('Opening Segment', html)
        self.assertIn('Main Mix', html)

    def test_music_library_template(self):
        """Test music library template generation"""
        library_data = {
            'statistics': {
                'total_tracks': 1500,
                'total_artists': 250,
                'avg_bpm': 125,
                'total_duration_hours': 125.5
            },
            'genres': {
                'House': 450,
                'Techno': 380,
                'Trance': 200,
                'Ambient': 150
            },
            'top_artists': [
                {
                    'name': 'Artist 1',
                    'track_count': 25,
                    'avg_bpm': 128,
                    'dominant_key': 'Am'
                },
                {
                    'name': 'Artist 2',
                    'track_count': 18,
                    'avg_bpm': 124,
                    'dominant_key': 'C'
                }
            ]
        }

        html = self.templates.music_library_template(library_data)

        # Verify content
        self.assertIn('1500', html)  # Total tracks
        self.assertIn('250', html)   # Total artists
        self.assertIn('House', html)
        self.assertIn('450', html)   # House track count
        self.assertIn('Artist 1', html)

    def test_compatibility_matrix_template(self):
        """Test compatibility matrix template generation"""
        matrix_data = {
            'tracks': [
                {'name': 'Track A'},
                {'name': 'Track B'},
                {'name': 'Track C'}
            ],
            'scores': {
                '0_1': 0.85,
                '0_2': 0.45,
                '1_2': 0.92
            }
        }

        html = self.templates.compatibility_matrix_template(matrix_data)

        # Verify content
        self.assertIn('Track A', html)
        self.assertIn('Track B', html)
        self.assertIn('Track C', html)
        self.assertIn('matrix-table', html)
        self.assertIn('0.85', html)

    def test_analysis_summary_template(self):
        """Test analysis summary template generation"""
        summary_data = {
            'bpm_distribution': {
                '120-124': 15,
                '125-129': 25,
                '130-134': 10
            },
            'key_distribution': {
                'Am': 20,
                'C': 15,
                'G': 10
            }
        }

        html = self.templates.analysis_summary_template(summary_data)

        # Verify content
        self.assertIn('BPM Distribution', html)
        self.assertIn('120-124', html)
        self.assertIn('bar-chart', html)


if __name__ == '__main__':
    unittest.main()