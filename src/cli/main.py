"""Simple CLI for batch analysis and reporting."""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import os
from pathlib import Path
from typing import Iterable, List

from src.services.analyzer import Analyzer
from src.services.storage import Storage
from src.services.compatibility import suggest_compatible
from src.services.playlist import generate_playlist
from src.services.importers import import_mixedinkey_csv, import_rekordbox_xml, import_traktor_nml


AUDIO_EXTS = {".wav", ".mp3", ".flac", ".aac", ".ogg", ".m4a"}


def iter_audio_files(root: Path, exts: Iterable[str]) -> List[Path]:
    ex = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in exts}
    out: List[Path] = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if Path(fn).suffix.lower() in ex:
                out.append(Path(dirpath) / fn)
    return out


def cmd_analyze(args: argparse.Namespace) -> int:
    db = args.db or "data/music.db"
    storage = Storage.from_path(db)
    analyzer = Analyzer(storage, compute_hash=bool(args.hash))

    if args.path:
        analyzer.analyze_path(args.path)
        print(f"Analyzed: {args.path}")
        return 0

    root = Path(args.dir).resolve()
    exts = args.exts or list(AUDIO_EXTS)
    files = iter_audio_files(root, exts)
    if not files:
        print("No audio files found.")
        return 0
    print(f"Found {len(files)} files. Analyzing with {args.workers} workers...")
    root.mkdir(parents=True, exist_ok=True)

    def run(p: Path):
        try:
            analyzer.analyze_path(str(p))
            return (str(p), None)
        except Exception as e:
            return (str(p), str(e))

    errs = 0
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for fpath, err in pool.map(run, files):
            if err:
                errs += 1
                print(f"[ERR] {fpath}: {err}")
    ok = len(files) - errs
    print(f"Done. OK: {ok}, Errors: {errs}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    storage = Storage.from_path(args.db or "data/music.db")
    stats = storage.summary()
    print("Summary:")
    print(f"  Tracks: {stats['tracks']}")
    print(f"  With analysis: {stats['with_analysis']}")
    print(f"  Avg BPM: {stats['avg_bpm']:.2f}" if stats["avg_bpm"] is not None else "  Avg BPM: n/a")
    print("  Top Keys:")
    for k, c in stats["top_keys"]:
        print(f"    {k}: {c}")
    if args.csv:
        rows = storage.list_all_analyses()
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            f.write("path,bpm,key,energy,comment\n")
            for r in rows:
                path = r.get("path", "")
                bpm = r.get("bpm")
                key = r.get("key") or ""
                energy = r.get("energy")
                comment = (r.get("comment") or "").replace(",", " ")
                f.write(f"{path},{bpm if bpm is not None else ''},{key},{energy if energy is not None else ''},{comment}\n")
        print(f"CSV exported to {out}")
    return 0


def cmd_compat(args: argparse.Namespace) -> int:
    storage = Storage.from_path(args.db or "data/music.db")
    target = storage.get_analysis_by_path(args.path)
    if not target:
        print("Target track not found or not analyzed. Run 'analyze' first.")
        return 1
    all_rows = storage.list_all_analyses()
    # exclude self
    candidates = [r for r in all_rows if r.get("path") != target.get("path")]
    ranked = suggest_compatible(target, candidates, limit=args.top)
    print(f"Compatible for: {target['path']}")
    for i, r in enumerate(ranked, 1):
        print(f"{i:02d}. {r.get('path')} | BPM={r.get('bpm')} | Key={r.get('key')} | Energy={r.get('energy')}")
    return 0


def cmd_compat_export(args: argparse.Namespace) -> int:
    storage = Storage.from_path(args.db or "data/music.db")
    target = storage.get_analysis_by_path(args.path)
    if not target:
        print("Target track not found or not analyzed. Run 'analyze' first.")
        return 1
    all_rows = storage.list_all_analyses()
    candidates = [r for r in all_rows if r.get("path") != target.get("path")]
    ranked = suggest_compatible(target, candidates, limit=args.top)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    from src.services.compatibility import transition_score
    with out.open("w", encoding="utf-8") as f:
        f.write("path,bpm,key,energy,score\n")
        for r in ranked:
            sc = transition_score(target, r, prefer_rel=args.prefer_relative)
            f.write(f"{r.get('path','')},{r.get('bpm','')},{r.get('key','')},{r.get('energy','')},{sc:.2f}\n")
    print(f"Exported compatibility list to {out}")
    return 0


def cmd_playlist_generate(args: argparse.Namespace) -> int:
    storage = Storage.from_path(args.db or "data/music.db")
    seed = storage.get_analysis_by_path(args.seed)
    if not seed:
        print("Seed track not found or not analyzed. Run 'analyze' first.")
        return 1
    all_rows = storage.list_all_analyses()
    candidates = [r for r in all_rows if r.get("path") != seed.get("path")]
    pl = generate_playlist(seed, candidates, length=args.length, curve=args.curve)
    print(f"Playlist ({len(pl)} tracks) [curve={args.curve}] from: {seed['path']}")
    for i, r in enumerate(pl, 1):
        print(f"{i:02d}. {r.get('path')} | BPM={r.get('bpm')} | Key={r.get('key')} | Energy={r.get('energy')}")
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.suffix.lower() == ".csv":
            with out.open("w", encoding="utf-8") as f:
                f.write("path,bpm,key,energy\n")
                for r in pl:
                    path = r.get("path", "")
                    bpm = r.get("bpm")
                    key = r.get("key") or ""
                    energy = r.get("energy")
                    f.write(f"{path},{bpm if bpm is not None else ''},{key},{energy if energy is not None else ''}\n")
        else:
            with out.open("w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                # Try to include EXTINF duration in seconds and filename as title
                try:
                    import soundfile as sf
                except Exception:
                    sf = None
                try:
                    import librosa
                except Exception:
                    librosa = None
                for r in pl:
                    pth = r.get('path','')
                    dur = 0
                    try:
                        if sf:
                            info = sf.info(pth)
                            dur = int(info.duration)
                        elif librosa:
                            dur = int(librosa.get_duration(filename=pth))
                    except Exception:
                        dur = 0
                    title = Path(pth).name
                    f.write(f"#EXTINF:{dur},{title}\n{pth}\n")
        print(f"Exported to {out}")
    return 0


def cmd_import_mik(args: argparse.Namespace) -> int:
    storage = Storage.from_path(args.db or "data/music.db")
    n = import_mixedinkey_csv(args.csv, storage, root_dir=args.root)
    print(f"Imported {n} rows from {args.csv}")
    return 0


def cmd_import_rekordbox(args: argparse.Namespace) -> int:
    storage = Storage.from_path(args.db or "data/music.db")
    n = import_rekordbox_xml(args.xml, storage, root_dir=args.root)
    print(f"Imported {n} tracks from Rekordbox XML {args.xml}")
    return 0


def cmd_import_traktor(args: argparse.Namespace) -> int:
    storage = Storage.from_path(args.db or "data/music.db")
    n = import_traktor_nml(args.nml, storage, root_dir=args.root)
    print(f"Imported {n} tracks from Traktor NML {args.nml}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="music-cli", description="Music analysis CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_an = sub.add_parser("analyze", help="Analyze a file or a directory recursively")
    p_an.add_argument("--path", help="Path to a single audio file")
    p_an.add_argument("--dir", help="Directory with audio files")
    p_an.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_an.add_argument("--workers", type=int, default=1, help="Concurrent workers")
    p_an.add_argument("--hash", action="store_true", help="Compute file hash for cache validation")
    p_an.add_argument("--exts", nargs="+", help="Extensions to include (e.g., wav mp3 flac)")
    p_an.set_defaults(func=cmd_analyze)

    p_sm = sub.add_parser("summary", help="Show DB summary")
    p_sm.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_sm.add_argument("--csv", help="Export full analysis table to CSV path")
    p_sm.set_defaults(func=cmd_summary)

    p_cp = sub.add_parser("compat", help="Suggest compatible tracks for a given file")
    p_cp.add_argument("--path", required=True, help="Path to an analyzed track")
    p_cp.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_cp.add_argument("--top", type=int, default=10, help="How many suggestions to show")
    p_cp.set_defaults(func=cmd_compat)

    p_ce = sub.add_parser("compat-export", help="Export compatibility suggestions to CSV")
    p_ce.add_argument("--path", required=True, help="Path to an analyzed track")
    p_ce.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_ce.add_argument("--top", type=int, default=25, help="How many suggestions")
    p_ce.add_argument("--out", required=True, help="Output CSV path")
    p_ce.add_argument("--prefer-relative", action="store_true", help="Prefer relative major/minor in score")
    p_ce.set_defaults(func=cmd_compat_export)

    p_pl = sub.add_parser("playlist", help="Playlist operations")
    sp = p_pl.add_subparsers(dest="sub", required=True)
    p_gen = sp.add_parser("generate", help="Generate a playlist from a seed track and DB")
    p_gen.add_argument("--seed", required=True, help="Path to the seed track")
    p_gen.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_gen.add_argument("--length", type=int, default=10, help="Number of tracks in playlist")
    p_gen.add_argument("--curve", default="ascending", choices=["ascending", "descending", "flat"], help="Energy curve strategy")
    p_gen.add_argument("--out", help="Export playlist to file (.m3u or .csv)")
    p_gen.set_defaults(func=cmd_playlist_generate)

    p_imp = sub.add_parser("import-mik", help="Import MixedInKey-like CSV metadata into DB")
    p_imp.add_argument("--csv", required=True, help="Path to MixedInKey CSV")
    p_imp.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_imp.add_argument("--root", help="Optional root dir to prefix relative paths")
    p_imp.set_defaults(func=cmd_import_mik)

    p_irb = sub.add_parser("import-rekordbox", help="Import Rekordbox XML into DB")
    p_irb.add_argument("--xml", required=True, help="Rekordbox XML path")
    p_irb.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_irb.add_argument("--root", help="Optional root dir to prefix relative paths")
    p_irb.set_defaults(func=cmd_import_rekordbox)

    p_itr = sub.add_parser("import-traktor", help="Import Traktor NML into DB")
    p_itr.add_argument("--nml", required=True, help="Traktor NML collection path")
    p_itr.add_argument("--db", help="SQLite DB file (default data/music.db)")
    p_itr.add_argument("--root", help="Optional root dir to prefix relative paths")
    p_itr.set_defaults(func=cmd_import_traktor)

    return ap


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
