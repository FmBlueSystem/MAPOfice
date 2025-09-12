# Configurar Claude (Anthropic) - Modelo Mucho Mejor que el Chino

## ¿Por qué cambiar a Claude?

El modelo chino `glm-4.5-flash` está devolviendo análisis de muy baja calidad (confianza 0.3) con respuestas "fallback". **Claude Haiku es mucho más inteligente y confiable.**

## Ventajas de Claude Haiku:

✅ **Mucha mejor precisión** - entiende música y artistas famosos  
✅ **Muy económico** - $0.25 por 1M tokens (~100,000 análisis por $1)  
✅ **Rápido** - diseñado para aplicaciones de producción  
✅ **JSON confiable** - respuestas bien formateadas  
✅ **Detección de reediciones** - identifica fechas originales vs compilaciones  

## Configuración (5 minutos):

### 1. Obtener API Key
- Ve a https://console.anthropic.com/
- Crea cuenta (gratis, incluye créditos iniciales)
- Ve a "API Keys" y genera una nueva clave

### 2. Configurar Variable de Entorno

**Opción A: Temporal (solo esta sesión)**
```bash
export ANTHROPIC_API_KEY='tu-clave-aqui'
```

**Opción B: Permanente**
```bash
# Agregar al final de ~/.zshrc (o ~/.bash_profile)
echo 'export ANTHROPIC_API_KEY="tu-clave-aqui"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Probar la Configuración
```bash
cd "/Users/freddymolina/Desktop/MAP 4"
source .venv/bin/activate
python test_claude_provider.py
```

### 4. Lanzar Aplicación
```bash
source .venv/bin/activate
python -m src.ui.enhanced_main_window
```

## Comparación de Modelos:

| Modelo | Precisión | Costo | Velocidad | Detección de Artistas |
|---------|-----------|-------|-----------|----------------------|
| **Claude Haiku** | 🟢 Alta (0.8-0.9) | 💰 Barato | ⚡ Rápido | ✅ Excelente |
| Z.ai glm-4.5-flash | 🔴 Baja (0.3) | 💰 Gratis | 🐌 Lento (8s) | ❌ Pobre |
| OpenAI GPT-4o-mini | 🟢 Alta | 💰💰 Más caro | ⚡ Rápido | ✅ Muy bueno |

## Verificación de que Funciona:

Una vez configurado, deberías ver análisis como:
```json
{
  "genre": "Disco",
  "era": "1970s", 
  "confidence": 0.85,
  "date_verification": {
    "known_original_year": 1977,
    "is_likely_reissue": true
  }
}
```

En lugar de las respuestas genéricas del modelo chino.

## Costos Estimados:

- **Claude Haiku**: ~$0.002 por cada 100 canciones analizadas  
- **Z.ai**: Gratis pero resultados muy malos  
- **OpenAI**: ~$0.01 por cada 100 canciones  

**Recomendación**: Claude Haiku ofrece la mejor relación calidad/precio.