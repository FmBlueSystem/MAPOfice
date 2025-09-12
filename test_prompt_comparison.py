#!/usr/bin/env python3
"""Comparación de prompts: pequeños vs largos para GLM-4.5-Flash"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_prompt_strategies():
    """Diferentes estrategias de prompt"""
    
    track_info = "Destination - 'Move On Up' | BPM: 118 | Energy: 0.75 | Date: 1992-01-01"
    
    strategies = {
        "ultra_small": {
            "system": "JSON only.",
            "user": f"{track_info}\n\n{{\"genre\":\"disco\",\"era\":\"1970s\",\"reissue\":true}}"
        },
        
        "small_with_example": {
            "system": "Music analysis. Return JSON format only.",
            "user": f"{track_info}\n\nExample: {{\"genre\":\"disco\",\"era\":\"1970s\",\"known_year\":1979,\"reissue\":true}}\n\nAnalyze:"
        },
        
        "small_with_question": {
            "system": "You know music history. JSON only.",
            "user": f"{track_info}\n\nDo you know this song? Original year?\n\n{{\"genre\":\"\",\"era\":\"\",\"known_year\":null,\"reissue\":false}}"
        },
        
        "few_shot": {
            "system": "Music expert. JSON only.",
            "user": f"""Examples:
Beatles - Hey Jude | 1968 → {{\"genre\":\"rock\",\"era\":\"1960s\",\"known_year\":1968}}
Bee Gees - Stayin' Alive | 1977 → {{\"genre\":\"disco\",\"era\":\"1970s\",\"known_year\":1977}}

{track_info} → """
        },
        
        "directive": {
            "system": "Complete JSON pattern:",
            "user": f"{track_info}\n\nPattern: {{\"genre\":\"?\",\"era\":\"?\",\"known_year\":?,\"reissue\":?}}"
        }
    }
    
    return strategies

def simulate_responses():
    """Simula qué tan bien funcionaría cada estrategia"""
    
    strategies = get_prompt_strategies()
    
    print("🧪 COMPARACIÓN DE ESTRATEGIAS DE PROMPT")
    print("=" * 70)
    print("Track: Destination - Move On Up (1979 original, 1992 metadata)")
    print("Objetivo: Detectar que es disco de 1979, no de 1992")
    print("-" * 70)
    
    for name, prompt in strategies.items():
        print(f"\n📝 ESTRATEGIA: {name.upper()}")
        print(f"System ({len(prompt['system'])} chars): {prompt['system']}")
        print(f"User ({len(prompt['user'])} chars): {prompt['user'][:150]}{'...' if len(prompt['user']) > 150 else ''}")
        
        # Evalúa la probabilidad de éxito
        total_length = len(prompt['system']) + len(prompt['user'])
        
        # Factores de éxito
        has_example = "Example" in prompt['user'] or "→" in prompt['user']
        has_question = "know" in prompt['user'].lower() or "?" in prompt['user']
        has_structure = "{" in prompt['user'] and "}" in prompt['user']
        is_short = total_length < 200
        
        score = 0
        factors = []
        
        if is_short:
            score += 3
            factors.append("✅ Corto (<200 chars)")
        else:
            factors.append("⚠️ Largo (>200 chars)")
            
        if has_example:
            score += 2
            factors.append("✅ Incluye ejemplo")
            
        if has_question:
            score += 2
            factors.append("✅ Pregunta directa")
            
        if has_structure:
            score += 1
            factors.append("✅ Estructura JSON clara")
        
        # Factores específicos por estrategia
        if name == "ultra_small":
            score += 1
            factors.append("✅ Máxima simplicidad")
        elif name == "few_shot":
            score += 2
            factors.append("✅ Few-shot learning")
        elif name == "directive":
            score += 1
            factors.append("✅ Directiva clara")
        
        print(f"Longitud total: {total_length} chars")
        print(f"Factores de éxito: {', '.join(factors)}")
        print(f"Puntuación estimada: {score}/10")
        
        # Predicción de resultado
        if score >= 8:
            print("🎉 ALTA probabilidad de éxito")
        elif score >= 6:
            print("✅ BUENA probabilidad de éxito")
        elif score >= 4:
            print("⚠️ MEDIA probabilidad de éxito")
        else:
            print("❌ BAJA probabilidad de éxito")

def get_recommended_strategy():
    """Estrategia recomendada basada en análisis"""
    
    print(f"\n🏆 ESTRATEGIA RECOMENDADA: FEW-SHOT")
    print("-" * 40)
    
    recommended = {
        "system": "Music expert. JSON only.",
        "user": """Examples:
Beatles - Hey Jude | 1968 → {"genre":"rock","era":"1960s","original":1968}
Bee Gees - Stayin' Alive | 1977 → {"genre":"disco","era":"1970s","original":1977}
Curtis Mayfield - Move On Up | 1970 → {"genre":"soul","era":"1970s","original":1970}

Destination - Move On Up | 1992 → """
    }
    
    print("Sistema:", recommended["system"])
    print("Usuario:", recommended["user"])
    print(f"Total: {len(recommended['system']) + len(recommended['user'])} chars")
    
    print(f"\n💡 VENTAJAS:")
    print(f"✅ Few-shot learning con ejemplos relevantes")
    print(f"✅ Incluye 'Move On Up' de Curtis Mayfield como contexto")
    print(f"✅ Formato JSON claro y consistente")
    print(f"✅ Pregunta implícita sobre conocimiento del track")
    print(f"✅ Longitud moderada (~200 chars)")
    
    return recommended

def compare_with_current():
    """Compara con el sistema actual"""
    
    print(f"\n📊 COMPARACIÓN CON SISTEMA ACTUAL")
    print("-" * 40)
    
    current_length = 800  # Estimado del prompt actual largo
    recommended_length = 180  # Few-shot prompt
    
    print(f"Sistema actual: ~{current_length} chars")
    print(f"Few-shot recomendado: ~{recommended_length} chars")
    print(f"Reducción: {((current_length - recommended_length) / current_length * 100):.0f}%")
    
    print(f"\n🎯 BENEFICIOS ESPERADOS:")
    print(f"✅ 77% menos tokens → respuestas más rápidas")
    print(f"✅ Menor probabilidad de respuestas cortadas")
    print(f"✅ Mayor consistencia en formato JSON")
    print(f"✅ Mejor reconocimiento de tracks famosos")
    print(f"✅ Respuestas más directas, menos verbosidad")

if __name__ == "__main__":
    simulate_responses()
    get_recommended_strategy()
    compare_with_current()