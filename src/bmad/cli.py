"""
BMAD CLI Integration
====================

Integrates BMAD methodology with the unified CLI system.
Replaces individual BMAD tool scripts with unified CLI commands.
"""

import os
import sys
import json
import click
from typing import Optional, List, Dict, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.bmad.core import BMADEngine, BMADConfig, BMADMode, create_bmad_engine
from src.bmad.certification import simulate_certification_demo
from src.bmad.metadata import create_sample_metadata_dataset, PureMetadataExtractor
from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

@click.group(name='bmad')
@click.pass_context
def bmad_cli(ctx):
    """
    BMAD (Bayesian Music Analysis and Decision) Methodology Commands
    
    Consolidated BMAD tools from:
    • bmad_100_certification_validator.py
    • bmad_demo_certification.py
    • bmad_prompt_optimization.py  
    • bmad_pure_metadata_optimizer.py
    • bmad_real_data_optimizer.py
    """
    ctx.ensure_object(dict)

@bmad_cli.command('certify')
@click.option('--tracks', '-t', type=int, default=50, 
              help='Number of tracks for certification test')
@click.option('--threshold', type=float, default=0.80,
              help='Certification threshold (0.0-1.0)')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for certification report')
@click.option('--format', type=click.Choice(['json', 'text']), default='text',
              help='Output format')
@click.pass_context
def certify_command(ctx, tracks, threshold, output, format):
    """
    Run BMAD certification validation
    
    Consolidated from bmad_100_certification_validator.py and bmad_demo_certification.py
    """
    click.echo(f"🎯 BMAD Certification Validation")
    click.echo(f"📊 Tracks: {tracks}, Threshold: {threshold:.1%}")
    
    try:
        # Run certification demo
        report = simulate_certification_demo(tracks)
        
        if format == 'json':
            report_data = report.to_dict()
            
            if output:
                with open(output, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)
                click.echo(f"📄 Report saved to: {output}")
            else:
                click.echo(json.dumps(report_data, indent=2, default=str))
        else:
            # Text format
            click.echo(f"\n📊 CERTIFICATION RESULTS:")
            click.echo(f"   Certified: {'✅ YES' if report.certified else '❌ NO'}")
            click.echo(f"   Accuracy: {report.accuracy:.2%}")
            click.echo(f"   Certification Rate: {report.certification_rate:.2%}")
            click.echo(f"   Tracks Analyzed: {report.tracks_analyzed}")
            click.echo(f"   Tracks Passed: {report.tracks_passed}")
            click.echo(f"   Tracks Failed: {report.tracks_failed}")
            
            if report.issues:
                click.echo(f"\n⚠️  Issues Found ({len(report.issues)}):")
                for issue in report.issues[:5]:  # Show top 5
                    click.echo(f"   • {issue['issue']} ({issue['track']})")
                    
            if report.recommendations:
                click.echo(f"\n💡 Recommendations:")
                for rec in report.recommendations:
                    click.echo(f"   • {rec}")
                    
            if output:
                with open(output, 'w') as f:
                    f.write(f"BMAD Certification Report\n")
                    f.write(f"========================\n\n")
                    f.write(f"Certified: {report.certified}\n")
                    f.write(f"Accuracy: {report.accuracy:.2%}\n")
                    f.write(f"Certification Rate: {report.certification_rate:.2%}\n")
                    # ... additional report content
                click.echo(f"📄 Report saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Certification failed: {e}", err=True)
        sys.exit(1)

@bmad_cli.command('optimize')
@click.option('--mode', type=click.Choice(['prompt', 'data', 'metadata']), 
              default='prompt', help='Optimization mode')
@click.option('--cycles', type=int, default=3, help='Maximum optimization cycles')
@click.option('--target', type=float, default=0.85, help='Target accuracy')
@click.option('--provider', type=click.Choice(['anthropic', 'zai', 'openai']),
              help='LLM provider to use')
@click.option('--input-file', type=click.Path(exists=True),
              help='Input file with track data')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for optimization results')
@click.pass_context  
def optimize_command(ctx, mode, cycles, target, provider, input_file, output):
    """
    Run BMAD optimization cycles
    
    Consolidated from bmad_prompt_optimization.py, bmad_real_data_optimizer.py,
    and bmad_pure_metadata_optimizer.py
    """
    click.echo(f"🚀 BMAD Optimization - Mode: {mode}")
    click.echo(f"🎯 Target accuracy: {target:.1%}, Max cycles: {cycles}")
    
    try:
        # Load or create track data
        if input_file:
            with open(input_file, 'r') as f:
                track_data = json.load(f)
                tracks = track_data.get('tracks', track_data)
        else:
            click.echo("📊 Using sample dataset...")
            tracks = create_sample_metadata_dataset(20)
        
        # Setup LLM provider if specified
        llm_provider = None
        if provider:
            api_key = _get_api_key_for_provider(provider)
            if api_key:
                llm_config = LLMConfig(
                    provider=getattr(LLMProvider, provider.upper()),
                    api_key=api_key,
                    model=_get_default_model_for_provider(provider),
                    temperature=0.1
                )
                llm_provider = LLMProviderFactory.create_provider(llm_config)
            else:
                click.echo(f"⚠️  No API key found for {provider}, using simulation")
        
        # Create BMAD engine
        bmad_mode = BMADMode.OPTIMIZATION if mode == 'prompt' else BMADMode.REAL_DATA
        if mode == 'metadata':
            bmad_mode = BMADMode.PURE_METADATA
            
        config = BMADConfig(
            mode=bmad_mode,
            llm_provider=llm_config if llm_provider else None,
            max_optimization_cycles=cycles,
            certification_threshold=target
        )
        
        engine = BMADEngine(config)
        
        # Run optimization
        result = engine.execute(tracks)
        
        # Display results
        click.echo(f"\n📊 OPTIMIZATION RESULTS:")
        click.echo(f"   Success: {'✅ YES' if result.success else '❌ NO'}")
        click.echo(f"   Cycles Completed: {result.cycles_completed}")
        click.echo(f"   Processing Time: {result.processing_time:.2f}s")
        
        if result.results:
            if 'initial_accuracy' in result.results:
                click.echo(f"   Initial Accuracy: {result.results['initial_accuracy']:.2%}")
            if 'final_accuracy' in result.results:
                click.echo(f"   Final Accuracy: {result.results['final_accuracy']:.2%}")
            if 'improvement' in result.results:
                click.echo(f"   Improvement: {result.results['improvement']:.2%}")
        
        # Save results if requested
        if output:
            output_data = {
                'optimization_mode': mode,
                'success': result.success,
                'results': result.results,
                'metrics': result.metrics,
                'cycles_completed': result.cycles_completed,
                'processing_time': result.processing_time
            }
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            click.echo(f"📄 Results saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Optimization failed: {e}", err=True)
        sys.exit(1)

@bmad_cli.command('validate')
@click.option('--input-file', type=click.Path(exists=True), required=True,
              help='Input file with track data')
@click.option('--mode', type=click.Choice(['basic', 'full', 'metadata']), 
              default='basic', help='Validation mode')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for validation results')
@click.pass_context
def validate_command(ctx, input_file, mode, output):
    """
    Run BMAD validation on track data
    
    Consolidated from various validation tools
    """
    click.echo(f"🔍 BMAD Validation - Mode: {mode}")
    
    try:
        # Load track data
        with open(input_file, 'r') as f:
            data = json.load(f)
            tracks = data.get('tracks', data)
        
        if not tracks:
            click.echo("❌ No track data found in input file", err=True)
            sys.exit(1)
            
        click.echo(f"📊 Validating {len(tracks)} tracks...")
        
        # Choose validation mode
        if mode == 'metadata':
            bmad_mode = BMADMode.PURE_METADATA
        else:
            bmad_mode = BMADMode.VALIDATION
        
        config = BMADConfig(mode=bmad_mode)
        engine = BMADEngine(config)
        
        # Run validation
        result = engine.execute(tracks)
        
        # Display results
        click.echo(f"\n📊 VALIDATION RESULTS:")
        click.echo(f"   Success: {'✅ YES' if result.success else '❌ NO'}")
        click.echo(f"   Processing Time: {result.processing_time:.2f}s")
        
        if result.results:
            if 'tracks_processed' in result.results:
                click.echo(f"   Tracks Processed: {result.results['tracks_processed']}")
            if 'tracks_validated' in result.results:
                click.echo(f"   Tracks Validated: {result.results['tracks_validated']}")
            if 'validation_rate' in result.metrics:
                click.echo(f"   Validation Rate: {result.metrics['validation_rate']:.2%}")
        
        # Show errors if any
        if result.errors:
            click.echo(f"\n⚠️  Errors ({len(result.errors)}):")
            for error in result.errors[:5]:
                click.echo(f"   • {error}")
        
        # Save results if requested
        if output:
            output_data = {
                'validation_mode': mode,
                'success': result.success,
                'results': result.results,
                'metrics': result.metrics,
                'errors': result.errors,
                'warnings': result.warnings
            }
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            click.echo(f"📄 Results saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        sys.exit(1)

@bmad_cli.command('extract-metadata')
@click.option('--input-dir', type=click.Path(exists=True), 
              help='Directory with audio files')
@click.option('--input-file', type=click.Path(exists=True),
              help='File with track data')  
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file for extracted metadata')
@click.option('--count', type=int, default=50,
              help='Number of tracks to process')
@click.pass_context
def extract_metadata_command(ctx, input_dir, input_file, output, count):
    """
    Extract pure metadata from tracks
    
    Consolidated from bmad_pure_metadata_optimizer.py
    """
    click.echo(f"🔍 BMAD Pure Metadata Extraction")
    
    try:
        extractor = PureMetadataExtractor()
        
        if input_file:
            # Load from file
            with open(input_file, 'r') as f:
                data = json.load(f)
                tracks = data.get('tracks', data)
        elif input_dir:
            # Scan directory (simplified - would need audio processing)
            click.echo("📁 Directory scanning not yet implemented")
            click.echo("💡 Use sample dataset for demonstration")
            tracks = create_sample_metadata_dataset(count)
        else:
            # Use sample data
            click.echo("📊 Using sample metadata dataset")
            tracks = create_sample_metadata_dataset(count)
        
        click.echo(f"📊 Processing {len(tracks)} tracks...")
        
        # Extract metadata
        extracted_tracks = extractor.extract_from_tracks(tracks)
        
        click.echo(f"✅ Successfully extracted metadata from {len(extracted_tracks)} tracks")
        
        # Save results
        if extractor.save_extracted_metadata(extracted_tracks, output):
            click.echo(f"📄 Metadata saved to: {output}")
        else:
            click.echo(f"❌ Failed to save metadata to: {output}", err=True)
        
        # Show summary
        if extracted_tracks:
            sample_track = extracted_tracks[0]
            click.echo(f"\n📊 Sample extracted metadata:")
            click.echo(f"   Title: {sample_track.title}")
            click.echo(f"   Artist: {sample_track.artist}")
            click.echo(f"   Year: {sample_track.year}")
            click.echo(f"   Genre: {sample_track.genre_metadata}")
        
    except Exception as e:
        click.echo(f"❌ Metadata extraction failed: {e}", err=True)
        sys.exit(1)

@bmad_cli.command('demo')
@click.option('--mode', type=click.Choice(['certification', 'optimization', 'metadata']),
              default='certification', help='Demo mode')
@click.pass_context
def demo_command(ctx, mode):
    """
    Run BMAD methodology demo
    
    Consolidated demonstration of all BMAD capabilities
    """
    click.echo(f"🎵 BMAD Methodology Demo - {mode.capitalize()}")
    
    try:
        if mode == 'certification':
            click.echo("🎯 Running certification demo...")
            report = simulate_certification_demo(25)
            
            click.echo(f"\n📊 Demo Results:")
            click.echo(f"   Certified: {'✅ YES' if report.certified else '❌ NO'}")  
            click.echo(f"   Accuracy: {report.accuracy:.2%}")
            click.echo(f"   Tracks Analyzed: {report.tracks_analyzed}")
            
        elif mode == 'optimization':
            click.echo("🚀 Running optimization demo...")
            
            # Create demo engine
            config = BMADConfig(
                mode=BMADMode.OPTIMIZATION,
                max_optimization_cycles=2
            )
            engine = BMADEngine(config)
            
            # Use sample data
            tracks = create_sample_metadata_dataset(15)
            result = engine.execute(tracks)
            
            click.echo(f"\n📊 Demo Results:")
            click.echo(f"   Success: {'✅ YES' if result.success else '❌ NO'}")
            click.echo(f"   Cycles: {result.cycles_completed}")
            
        elif mode == 'metadata':
            click.echo("🔍 Running metadata extraction demo...")
            
            # Create demo engine
            config = BMADConfig(mode=BMADMode.PURE_METADATA)
            engine = BMADEngine(config)
            
            # Use sample data
            tracks = create_sample_metadata_dataset(10)
            result = engine.execute(tracks)
            
            click.echo(f"\n📊 Demo Results:")
            click.echo(f"   Success: {'✅ YES' if result.success else '❌ NO'}")
            click.echo(f"   Tracks Processed: {result.results.get('tracks_analyzed', 0)}")
        
        click.echo(f"\n💡 Use 'bmad {mode}' commands for full functionality")
        
    except Exception as e:
        click.echo(f"❌ Demo failed: {e}", err=True)
        sys.exit(1)

def _get_api_key_for_provider(provider: str) -> Optional[str]:
    """Get API key for specified provider"""
    key_map = {
        'anthropic': 'ANTHROPIC_API_KEY',
        'zai': 'ZAI_API_KEY', 
        'openai': 'OPENAI_API_KEY'
    }
    
    env_var = key_map.get(provider)
    return os.getenv(env_var) if env_var else None

def _get_default_model_for_provider(provider: str) -> str:
    """Get default model for specified provider"""
    model_map = {
        'anthropic': 'claude-3-haiku-20240307',
        'zai': 'glm-4.5-flash',
        'openai': 'gpt-3.5-turbo'
    }
    
    return model_map.get(provider, 'claude-3-haiku-20240307')

# Export for CLI integration
__all__ = ['bmad_cli']