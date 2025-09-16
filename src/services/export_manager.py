"""
Professional Export System for MAP4
Handles export to multiple formats: PDF, Excel/CSV, JSON
With customizable templates and batch processing
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import html
import base64
from io import BytesIO

class ExportManager:
    """Professional export system with multiple format support"""

    def __init__(self, export_dir: str = "exports"):
        """Initialize export manager with output directory"""
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)

        # Create subdirectories for different export types
        self.pdf_dir = self.export_dir / "pdf"
        self.excel_dir = self.export_dir / "excel"
        self.json_dir = self.export_dir / "json"
        self.reports_dir = self.export_dir / "reports"

        for dir in [self.pdf_dir, self.excel_dir, self.json_dir, self.reports_dir]:
            dir.mkdir(exist_ok=True)

    def export_to_json(self, data: Dict[str, Any], filename: str = None,
                      pretty: bool = True) -> Path:
        """Export data to JSON format"""
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.json_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        return filepath

    def export_to_csv(self, data: List[Dict], filename: str = None,
                     columns: List[str] = None) -> Path:
        """Export data to CSV format"""
        if not data:
            raise ValueError("No data to export")

        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = self.excel_dir / filename

        # Determine columns if not provided
        if columns is None:
            columns = list(data[0].keys())

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)

        return filepath

    def export_analysis_report(self, tracks: List[Dict],
                              title: str = "Music Analysis Report",
                              format: str = "html") -> Path:
        """Export comprehensive analysis report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        filepath = self.reports_dir / filename

        if format == "html":
            html_content = self._generate_html_report(tracks, title, timestamp)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
        elif format == "json":
            report_data = {
                "title": title,
                "timestamp": timestamp,
                "total_tracks": len(tracks),
                "tracks": tracks
            }
            return self.export_to_json(report_data, filename)
        elif format == "csv":
            # Flatten track data for CSV export
            flattened = []
            for track in tracks:
                flat_track = self._flatten_dict(track)
                flattened.append(flat_track)
            return self.export_to_csv(flattened, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return filepath

    def export_playlist_analysis(self, playlist_data: Dict,
                                 format: str = "html") -> Path:
        """Export playlist analysis with compatibility scores"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"playlist_{playlist_data.get('name', 'analysis')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        filepath = self.reports_dir / filename

        if format == "html":
            html_content = self._generate_playlist_html(playlist_data, timestamp)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
        elif format == "json":
            playlist_data['export_timestamp'] = timestamp
            return self.export_to_json(playlist_data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return filepath

    def batch_export(self, data_sets: List[Dict],
                    formats: List[str] = ["json", "csv", "html"]) -> Dict[str, List[Path]]:
        """Batch export multiple datasets in multiple formats"""
        results = {format: [] for format in formats}

        for i, data_set in enumerate(data_sets):
            name = data_set.get('name', f'dataset_{i}')
            data = data_set.get('data', [])

            for format in formats:
                if format == "json":
                    path = self.export_to_json(data, f"{name}.json")
                    results["json"].append(path)
                elif format == "csv" and isinstance(data, list):
                    path = self.export_to_csv(data, f"{name}.csv")
                    results["csv"].append(path)
                elif format == "html":
                    path = self.export_analysis_report(
                        data if isinstance(data, list) else [data],
                        title=name,
                        format="html"
                    )
                    results["html"].append(path)

        return results

    def _generate_html_report(self, tracks: List[Dict], title: str, timestamp: str) -> str:
        """Generate HTML report with professional styling"""
        track_rows = ""
        for i, track in enumerate(tracks, 1):
            # Extract key information
            name = track.get('name', 'Unknown')
            artist = track.get('artist', 'Unknown')
            bpm = track.get('bpm', 'N/A')
            key = track.get('key', 'N/A')
            energy = track.get('energy', 0)

            # HAMMS data if available
            hamms = track.get('hamms', {})
            hamms_score = hamms.get('overall_score', 'N/A') if hamms else 'N/A'

            # Format energy value
            energy_str = f"{energy:.2f}" if isinstance(energy, (int, float)) else str(energy)

            track_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(str(name))}</td>
                <td>{html.escape(str(artist))}</td>
                <td>{bpm}</td>
                <td>{key}</td>
                <td>{energy_str}</td>
                <td>{hamms_score}</td>
            </tr>
            """

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{html.escape(title)}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}

                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}

                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}

                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}

                .header p {{
                    opacity: 0.9;
                    font-size: 1.1em;
                }}

                .stats {{
                    display: flex;
                    justify-content: space-around;
                    padding: 30px;
                    background: #f8f9fa;
                    border-bottom: 1px solid #dee2e6;
                }}

                .stat-card {{
                    text-align: center;
                }}

                .stat-card .value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }}

                .stat-card .label {{
                    color: #6c757d;
                    margin-top: 5px;
                }}

                .content {{
                    padding: 40px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}

                thead {{
                    background: #f8f9fa;
                }}

                th {{
                    padding: 15px;
                    text-align: left;
                    font-weight: 600;
                    color: #495057;
                    border-bottom: 2px solid #dee2e6;
                }}

                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #dee2e6;
                }}

                tr:hover {{
                    background: #f8f9fa;
                }}

                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 0.9em;
                }}

                .badge {{
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-size: 0.85em;
                    font-weight: 500;
                }}

                .badge-success {{
                    background: #d4edda;
                    color: #155724;
                }}

                .badge-warning {{
                    background: #fff3cd;
                    color: #856404;
                }}

                @media print {{
                    body {{
                        background: white;
                    }}
                    .container {{
                        box-shadow: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎵 {html.escape(title)}</h1>
                    <p>Generated on {timestamp}</p>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="value">{len(tracks)}</div>
                        <div class="label">Total Tracks</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">{len(set(t.get('artist', '') for t in tracks))}</div>
                        <div class="label">Unique Artists</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">{sum(1 for t in tracks if t.get('bpm'))}</div>
                        <div class="label">Analyzed Tracks</div>
                    </div>
                </div>

                <div class="content">
                    <h2>Track Analysis Details</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Track Name</th>
                                <th>Artist</th>
                                <th>BPM</th>
                                <th>Key</th>
                                <th>Energy</th>
                                <th>HAMMS Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            {track_rows}
                        </tbody>
                    </table>
                </div>

                <div class="footer">
                    <p>MAP4 - Music Analyzer Pro | Professional Export System</p>
                    <p>© 2024 MAP4 Project. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html_template

    def _generate_playlist_html(self, playlist_data: Dict, timestamp: str) -> str:
        """Generate HTML report for playlist analysis"""
        name = playlist_data.get('name', 'Playlist')
        tracks = playlist_data.get('tracks', [])
        compatibility_matrix = playlist_data.get('compatibility_matrix', {})

        track_rows = ""
        for i, track in enumerate(tracks, 1):
            track_name = track.get('name', 'Unknown')
            bpm = track.get('bpm', 'N/A')
            key = track.get('key', 'N/A')

            # Get compatibility with next track
            compatibility = ""
            if i < len(tracks):
                next_track = tracks[i]
                compat_score = compatibility_matrix.get(f"{i-1}_{i}", {}).get('score', 'N/A')
                compatibility = f"{compat_score:.2f}" if isinstance(compat_score, (int, float)) else compat_score

            track_rows += f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(str(track_name))}</td>
                <td>{bpm}</td>
                <td>{key}</td>
                <td>{compatibility}</td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{html.escape(name)} - Playlist Analysis</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background: #667eea;
                    color: white;
                }}
                tr:hover {{
                    background: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎵 {html.escape(name)}</h1>
                <p>Generated: {timestamp}</p>
                <p>Total Tracks: {len(tracks)}</p>

                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Track</th>
                            <th>BPM</th>
                            <th>Key</th>
                            <th>Compatibility</th>
                        </tr>
                    </thead>
                    <tbody>
                        {track_rows}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary for CSV export"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    def create_custom_template(self, template_name: str, template_content: str) -> Path:
        """Create custom export template"""
        templates_dir = self.export_dir / "templates"
        templates_dir.mkdir(exist_ok=True)

        template_path = templates_dir / f"{template_name}.html"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)

        return template_path

    def export_with_branding(self, data: Any, format: str,
                           brand_config: Dict) -> Path:
        """Export with custom branding options"""
        # Extract branding configuration
        logo = brand_config.get('logo', '')
        colors = brand_config.get('colors', {})
        company_name = brand_config.get('company_name', 'MAP4')

        # Modify export based on branding
        if format == "html":
            # Add custom styling and branding to HTML
            pass

        # Proceed with regular export
        return self.export_analysis_report(data, title=company_name, format=format)