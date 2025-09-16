"""
Professional Export Templates for MAP4
Customizable templates for different export scenarios
"""

from typing import Dict, List, Any
from datetime import datetime
import html
import json

class ExportTemplates:
    """Collection of professional export templates"""

    @staticmethod
    def dj_setlist_template(tracks: List[Dict], event_info: Dict = None) -> str:
        """Template for DJ setlist exports"""
        event_name = event_info.get('name', 'DJ Set') if event_info else 'DJ Set'
        venue = event_info.get('venue', '') if event_info else ''
        date = event_info.get('date', datetime.now().strftime('%Y-%m-%d')) if event_info else datetime.now().strftime('%Y-%m-%d')

        track_list = ""
        total_duration = 0
        current_time = 0

        for i, track in enumerate(tracks, 1):
            duration = track.get('duration', 0)
            time_marker = f"{current_time // 60:02d}:{current_time % 60:02d}"
            current_time += duration

            track_list += f"""
            <div class="track-item">
                <div class="track-number">{i}</div>
                <div class="track-info">
                    <div class="track-title">{html.escape(str(track.get('name', 'Unknown')))}</div>
                    <div class="track-artist">{html.escape(str(track.get('artist', 'Unknown')))}</div>
                </div>
                <div class="track-details">
                    <span class="time-marker">{time_marker}</span>
                    <span class="bpm">{track.get('bpm', 'N/A')} BPM</span>
                    <span class="key">{track.get('key', 'N/A')}</span>
                </div>
            </div>
            """
            total_duration += duration

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{html.escape(event_name)} - DJ Setlist</title>
            <style>
                body {{
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    background: #1a1a1a;
                    color: #fff;
                    margin: 0;
                    padding: 20px;
                }}

                .setlist-header {{
                    text-align: center;
                    padding: 40px 20px;
                    background: linear-gradient(135deg, #ff006e 0%, #8338ec 100%);
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}

                .setlist-header h1 {{
                    margin: 0;
                    font-size: 3em;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}

                .event-details {{
                    margin-top: 15px;
                    font-size: 1.2em;
                    opacity: 0.9;
                }}

                .track-list {{
                    max-width: 800px;
                    margin: 0 auto;
                }}

                .track-item {{
                    display: flex;
                    align-items: center;
                    background: #2a2a2a;
                    margin-bottom: 10px;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #ff006e;
                    transition: transform 0.2s;
                }}

                .track-item:hover {{
                    transform: translateX(5px);
                    background: #333;
                }}

                .track-number {{
                    font-size: 1.5em;
                    font-weight: bold;
                    width: 50px;
                    color: #ff006e;
                }}

                .track-info {{
                    flex: 1;
                    padding: 0 20px;
                }}

                .track-title {{
                    font-size: 1.2em;
                    font-weight: 500;
                    margin-bottom: 5px;
                }}

                .track-artist {{
                    color: #aaa;
                    font-size: 1em;
                }}

                .track-details {{
                    display: flex;
                    gap: 20px;
                    font-size: 0.9em;
                    color: #888;
                }}

                .track-details span {{
                    background: #1a1a1a;
                    padding: 5px 10px;
                    border-radius: 15px;
                }}

                .time-marker {{
                    color: #8338ec;
                }}

                .bpm {{
                    color: #ff006e;
                }}

                .key {{
                    color: #3cf;
                }}

                .summary {{
                    margin-top: 40px;
                    padding: 20px;
                    background: #2a2a2a;
                    border-radius: 10px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="setlist-header">
                <h1>{html.escape(event_name)}</h1>
                <div class="event-details">
                    {html.escape(venue) + ' | ' if venue else ''}{date}
                </div>
            </div>

            <div class="track-list">
                {track_list}
            </div>

            <div class="summary">
                <p>Total Tracks: {len(tracks)} | Duration: {total_duration // 60} minutes</p>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def radio_show_template(segments: List[Dict], show_info: Dict) -> str:
        """Template for radio show exports"""
        show_name = show_info.get('name', 'Radio Show')
        host = show_info.get('host', '')
        episode = show_info.get('episode', '')

        segment_html = ""
        for segment in segments:
            tracks_html = ""
            for track in segment.get('tracks', []):
                tracks_html += f"""
                <li>
                    <strong>{html.escape(str(track.get('artist', '')))}</strong> -
                    {html.escape(str(track.get('name', '')))}
                    <span class="track-meta">({track.get('duration_formatted', '')})</span>
                </li>
                """

            segment_html += f"""
            <div class="segment">
                <h3>{html.escape(segment.get('name', 'Segment'))}</h3>
                <div class="segment-time">{segment.get('start_time', '')} - {segment.get('end_time', '')}</div>
                <ul class="track-list">
                    {tracks_html}
                </ul>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{html.escape(show_name)} - Radio Show</title>
            <style>
                body {{
                    font-family: Georgia, serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #fafafa;
                    color: #333;
                }}

                .header {{
                    border-bottom: 3px double #333;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}

                h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}

                .show-info {{
                    margin-top: 10px;
                    color: #666;
                }}

                .segment {{
                    margin-bottom: 30px;
                    padding: 20px;
                    background: white;
                    border-left: 4px solid #4a90e2;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}

                .segment h3 {{
                    margin-top: 0;
                    color: #4a90e2;
                }}

                .segment-time {{
                    color: #888;
                    font-size: 0.9em;
                    margin-bottom: 15px;
                }}

                .track-list {{
                    list-style: none;
                    padding: 0;
                }}

                .track-list li {{
                    padding: 8px 0;
                    border-bottom: 1px dotted #ddd;
                }}

                .track-meta {{
                    color: #888;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{html.escape(show_name)}</h1>
                <div class="show-info">
                    {f'Hosted by {html.escape(host)}' if host else ''}
                    {f' | Episode {html.escape(str(episode))}' if episode else ''}
                </div>
            </div>

            {segment_html}
        </body>
        </html>
        """

    @staticmethod
    def music_library_template(library_data: Dict) -> str:
        """Template for music library analysis exports"""
        stats = library_data.get('statistics', {})
        genres = library_data.get('genres', {})
        top_artists = library_data.get('top_artists', [])[:10]

        genre_chart = ""
        for genre, count in genres.items():
            percentage = (count / stats.get('total_tracks', 1)) * 100
            genre_chart += f"""
            <div class="genre-item">
                <span class="genre-name">{html.escape(genre)}</span>
                <div class="genre-bar">
                    <div class="genre-fill" style="width: {percentage}%"></div>
                </div>
                <span class="genre-count">{count}</span>
            </div>
            """

        artists_html = ""
        for artist in top_artists:
            artists_html += f"""
            <tr>
                <td>{html.escape(str(artist.get('name', '')))}</td>
                <td>{artist.get('track_count', 0)}</td>
                <td>{artist.get('avg_bpm', 'N/A')}</td>
                <td>{artist.get('dominant_key', 'N/A')}</td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Music Library Analysis</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f7fa;
                }}

                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }}

                .stat-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                    text-align: center;
                }}

                .stat-value {{
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #4a5568;
                    display: block;
                }}

                .stat-label {{
                    color: #718096;
                    margin-top: 8px;
                    text-transform: uppercase;
                    font-size: 0.85em;
                    letter-spacing: 0.5px;
                }}

                .section {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                    margin-bottom: 30px;
                }}

                h2 {{
                    margin-top: 0;
                    color: #2d3748;
                    border-bottom: 2px solid #e2e8f0;
                    padding-bottom: 10px;
                }}

                .genre-item {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                }}

                .genre-name {{
                    width: 120px;
                    font-weight: 500;
                }}

                .genre-bar {{
                    flex: 1;
                    height: 25px;
                    background: #e2e8f0;
                    border-radius: 5px;
                    margin: 0 15px;
                    overflow: hidden;
                }}

                .genre-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    border-radius: 5px;
                }}

                .genre-count {{
                    width: 50px;
                    text-align: right;
                    color: #718096;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}

                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e2e8f0;
                }}

                th {{
                    background: #f7fafc;
                    font-weight: 600;
                    color: #4a5568;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Music Library Analysis Report</h1>

                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-value">{stats.get('total_tracks', 0)}</span>
                        <div class="stat-label">Total Tracks</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{stats.get('total_artists', 0)}</span>
                        <div class="stat-label">Artists</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{stats.get('avg_bpm', 0):.0f}</span>
                        <div class="stat-label">Avg BPM</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{stats.get('total_duration_hours', 0):.1f}h</span>
                        <div class="stat-label">Total Duration</div>
                    </div>
                </div>

                <div class="section">
                    <h2>Genre Distribution</h2>
                    {genre_chart}
                </div>

                <div class="section">
                    <h2>Top Artists</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Artist</th>
                                <th>Tracks</th>
                                <th>Avg BPM</th>
                                <th>Key</th>
                            </tr>
                        </thead>
                        <tbody>
                            {artists_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def compatibility_matrix_template(matrix_data: Dict) -> str:
        """Template for track compatibility matrix exports"""
        tracks = matrix_data.get('tracks', [])
        scores = matrix_data.get('scores', {})

        matrix_html = "<table class='matrix-table'><thead><tr><th></th>"

        # Headers
        for track in tracks:
            matrix_html += f"<th class='rotate'><div><span>{html.escape(str(track.get('name', ''))[:20])}</span></div></th>"
        matrix_html += "</tr></thead><tbody>"

        # Matrix rows
        for i, track1 in enumerate(tracks):
            matrix_html += f"<tr><th>{html.escape(str(track1.get('name', ''))[:20])}</th>"
            for j, track2 in enumerate(tracks):
                score = scores.get(f"{i}_{j}", 0)
                color_class = "high" if score > 0.8 else "medium" if score > 0.5 else "low"
                matrix_html += f"<td class='score {color_class}'>{score:.2f}</td>"
            matrix_html += "</tr>"

        matrix_html += "</tbody></table>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Track Compatibility Matrix</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px;
                    background: #1a1a2e;
                    color: #eee;
                }}

                h1 {{
                    text-align: center;
                    color: #fff;
                }}

                .matrix-table {{
                    margin: 0 auto;
                    border-collapse: collapse;
                    box-shadow: 0 0 20px rgba(0,0,0,0.5);
                }}

                .matrix-table th, .matrix-table td {{
                    width: 40px;
                    height: 40px;
                    text-align: center;
                    border: 1px solid #333;
                }}

                .matrix-table thead th {{
                    background: #16213e;
                    color: #fff;
                    font-size: 0.8em;
                }}

                .rotate {{
                    height: 140px;
                    white-space: nowrap;
                }}

                .rotate > div {{
                    transform: translate(0px, 51px) rotate(-45deg);
                    width: 30px;
                }}

                .rotate > div > span {{
                    padding: 5px 10px;
                }}

                .score {{
                    font-size: 0.75em;
                    font-weight: bold;
                }}

                .score.high {{
                    background: #27ae60;
                    color: white;
                }}

                .score.medium {{
                    background: #f39c12;
                    color: white;
                }}

                .score.low {{
                    background: #e74c3c;
                    color: white;
                }}

                .legend {{
                    margin-top: 30px;
                    text-align: center;
                }}

                .legend span {{
                    display: inline-block;
                    padding: 5px 15px;
                    margin: 0 10px;
                    border-radius: 3px;
                }}
            </style>
        </head>
        <body>
            <h1>Track Compatibility Matrix</h1>
            {matrix_html}
            <div class="legend">
                <span class="score high">High (>0.8)</span>
                <span class="score medium">Medium (0.5-0.8)</span>
                <span class="score low">Low (<0.5)</span>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def analysis_summary_template(summary_data: Dict) -> str:
        """Template for analysis summary with charts"""
        bpm_distribution = summary_data.get('bpm_distribution', {})
        key_distribution = summary_data.get('key_distribution', {})
        energy_timeline = summary_data.get('energy_timeline', [])

        # Create BPM chart
        bpm_chart = ""
        for range, count in bpm_distribution.items():
            bpm_chart += f"""
            <div class="bar-item">
                <div class="bar" style="height: {count * 10}px">
                    <span class="value">{count}</span>
                </div>
                <div class="label">{range}</div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Analysis Summary</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}

                .dashboard {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}

                .dashboard-header {{
                    background: rgba(255,255,255,0.95);
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}

                .chart-container {{
                    background: rgba(255,255,255,0.95);
                    padding: 25px;
                    border-radius: 15px;
                    margin-bottom: 20px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}

                .chart-title {{
                    font-size: 1.5em;
                    font-weight: 600;
                    margin-bottom: 20px;
                    color: #333;
                }}

                .bar-chart {{
                    display: flex;
                    align-items: flex-end;
                    justify-content: space-around;
                    height: 200px;
                    padding: 20px 0;
                }}

                .bar-item {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    flex: 1;
                }}

                .bar {{
                    width: 40px;
                    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
                    border-radius: 5px 5px 0 0;
                    position: relative;
                    display: flex;
                    align-items: flex-start;
                    justify-content: center;
                }}

                .bar .value {{
                    position: absolute;
                    top: -25px;
                    font-weight: bold;
                    color: #667eea;
                }}

                .label {{
                    margin-top: 10px;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="dashboard-header">
                    <h1>Music Analysis Summary</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>

                <div class="chart-container">
                    <div class="chart-title">BPM Distribution</div>
                    <div class="bar-chart">
                        {bpm_chart}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """