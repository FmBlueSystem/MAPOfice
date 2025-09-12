#!/usr/bin/env python3
"""
Test forzado para certificar escritura de metadatos con análisis nuevo
=====================================================================
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path  
sys.path.append('/Users/freddymolina/Desktop/MAP 4')

try:
    from src.services.enhanced_analyzer import create_enhanced_analyzer
    import mutagen
    from mutagen.flac import FLAC
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_force_new_analysis():
    """Test con análisis forzado y verificación completa"""
    
    # Crear analyzer sin validación y AI habilitado
    analyzer = create_enhanced_analyzer()
    analyzer.skip_validation = True
    
    # Archivo de prueba
    test_file = "/Volumes/My Passport/Abibleoteca/Consolidado2025/Tracks/'Til Tuesday - Love in a Vacuum.flac"
    
    print(f"🎯 INICIANDO TEST FORZADO CON: {Path(test_file).name}")
    print("=" * 70)
    
    # Verificar estado inicial
    print("\n📏 ESTADO INICIAL:")
    if os.path.exists(test_file):
        stat_before = os.stat(test_file)
        print(f"  🕒 Timestamp: {time.ctime(stat_before.st_mtime)}")
        print(f"  📁 Size: {stat_before.st_size:,} bytes")
        
        # Leer metadatos actuales
        try:
            audio = FLAC(test_file)
            print(f"  🏷️  Total tags: {len(audio)}")
            print(f"  🤖 AI Genre: {audio.get('GENRE')}")
            print(f"  🤖 AI Subgenre: {audio.get('SUBGENRE')}")
            print(f"  🤖 AI Mood: {audio.get('MOOD')}")
            print(f"  🤖 AI Era: {audio.get('ERA')}")
        except Exception as e:
            print(f"  ⚠️ Error reading metadata: {e}")
    else:
        print(f"  ❌ File not found: {test_file}")
        return
    
    # EJECUTAR ANÁLISIS FORZADO (ignorar caché)
    print(f"\n🔄 EJECUTANDO ANÁLISIS FORZADO...")
    print("-" * 40)
    
    result = analyzer.analyze_track(test_file, force_reanalysis=True)
    
    if result.success:
        print(f"✅ Análisis exitoso!")
        print(f"  🎵 Genre: {result.genre}")
        print(f"  🎵 Subgenre: {result.subgenre}")
        print(f"  😊 Mood: {result.mood}")
        print(f"  📅 Era: {result.era}")
        print(f"  🤖 AI Confidence: {result.ai_confidence}")
    else:
        print(f"❌ Análisis falló: {result.error_message}")
        return
    
    # Verificar estado después del análisis
    print(f"\n📏 ESTADO DESPUÉS DEL ANÁLISIS:")
    stat_after = os.stat(test_file)
    print(f"  🕒 Timestamp: {time.ctime(stat_after.st_mtime)}")
    print(f"  📁 Size: {stat_after.st_size:,} bytes")
    
    # Leer metadatos actuales
    try:
        audio = FLAC(test_file)
        print(f"  🏷️  Total tags: {len(audio)}")
        
        actual_genre = audio.get('GENRE', [None])[0] if 'GENRE' in audio else None
        actual_subgenre = audio.get('SUBGENRE', [None])[0] if 'SUBGENRE' in audio else None
        actual_mood = audio.get('MOOD', [None])[0] if 'MOOD' in audio else None
        actual_era = audio.get('ERA', [None])[0] if 'ERA' in audio else None
        actual_ai_analyzed = audio.get('AI_ANALYZED', [None])[0] if 'AI_ANALYZED' in audio else None
        
        print(f"  🤖 AI Genre: {actual_genre}")
        print(f"  🤖 AI Subgenre: {actual_subgenre}")
        print(f"  🤖 AI Mood: {actual_mood}")
        print(f"  🤖 AI Era: {actual_era}")
        print(f"  🤖 AI Analyzed: {actual_ai_analyzed}")
        
    except Exception as e:
        print(f"  ⚠️ Error reading metadata: {e}")
        return
    
    # VERIFICACIÓN DE CORRESPONDENCIA
    print(f"\n🔍 VERIFICACIÓN DE CORRESPONDENCIA:")
    print("-" * 35)
    
    file_modified = stat_after.st_mtime != stat_before.st_mtime
    metadata_written = actual_ai_analyzed is not None
    genre_matches = result.genre == actual_genre
    subgenre_matches = result.subgenre == actual_subgenre
    mood_matches = result.mood == actual_mood
    era_matches = result.era == actual_era
    
    print(f"  🕒 File modified: {file_modified} {'✅' if file_modified else '❌'}")
    print(f"  📝 Metadata written: {metadata_written} {'✅' if metadata_written else '❌'}")
    print(f"  🎵 Genre match: {genre_matches} {'✅' if genre_matches else '❌'}")
    print(f"  🎵 Subgenre match: {subgenre_matches} {'✅' if subgenre_matches else '❌'}")
    print(f"  😊 Mood match: {mood_matches} {'✅' if mood_matches else '❌'}")
    print(f"  📅 Era match: {era_matches} {'✅' if era_matches else '❌'}")
    
    # DECISIÓN FINAL
    print(f"\n⚖️  DECISIÓN FINAL:")
    print("-" * 20)
    
    matches = sum([genre_matches, subgenre_matches, mood_matches, era_matches])
    score = matches / 4.0
    
    if file_modified and metadata_written and score >= 0.75:
        print("🎉 CERTIFICACIÓN: APROBADA")
        print("   ✅ El archivo fue modificado")
        print("   ✅ Los metadatos fueron escritos") 
        print("   ✅ La correspondencia es válida")
        print(f"   📊 Score: {score:.2%}")
        return True
    else:
        print("❌ CERTIFICACIÓN: FALLA")
        if not file_modified:
            print("   ❌ El archivo NO fue modificado")
        if not metadata_written:
            print("   ❌ Los metadatos NO fueron escritos")
        if score < 0.75:
            print(f"   ❌ Correspondencia insuficiente ({score:.2%})")
        return False


if __name__ == "__main__":
    result = test_force_new_analysis()
    print(f"\n{'='*70}")
    print(f"RESULTADO FINAL: {'ÉXITO' if result else 'FALLA'}")
    print(f"{'='*70}")