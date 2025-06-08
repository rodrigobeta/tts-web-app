# backend/tts_engine.py
import os
import uuid
import torch
import yaml
import numpy as np
from typing import Union, Optional
from string import punctuation
from model import FastSpeech2
from utils.model import get_vocoder
from utils.tools import to_device, synth_samples
from text import text_to_sequence
from g2p_en import G2p
from pypinyin import pinyin, Style
import re
from utils.tools import synth_samples
import tempfile
import shutil

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configuración de rutas - Ajusta estas rutas según tu estructura de archivos
CONFIG_PREPROCESS_PATH = os.path.join(BASE_DIR, "config/LJSpeech/preprocess.yaml")
CONFIG_MODEL_PATH = os.path.join(BASE_DIR, "config/LJSpeech/model.yaml")
CONFIG_TRAIN_PATH = os.path.join(BASE_DIR, "config/LJSpeech/train.yaml")
CHECKPOINT_PATH = os.path.join(BASE_DIR, "output/ckpt/LJSpeech/900000.pth.tar")

# Cargar configuraciones
with open(CONFIG_PREPROCESS_PATH, 'r') as f:
    preprocess_config = yaml.load(f, Loader=yaml.FullLoader)
with open(CONFIG_MODEL_PATH, 'r') as f:
    model_config = yaml.load(f, Loader=yaml.FullLoader)
with open(CONFIG_TRAIN_PATH, 'r') as f:
    train_config = yaml.load(f, Loader=yaml.FullLoader)

# Inicializar modelo y vocoder (una sola vez)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = FastSpeech2(preprocess_config, model_config).to(device)
model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=device)['model'])
model.eval()
model.requires_grad_ = False

vocoder = get_vocoder(model_config, device)

def preprocess_text(text: str, preprocess_config: dict) -> tuple:
    """Preprocesa el texto para la síntesis."""
    if preprocess_config["preprocessing"]["text"]["language"] == "en":
        # Procesamiento para inglés
        g2p = G2p()
        phones = g2p(text)
        phones = " ".join(phones)
        sequence = np.array(text_to_sequence(phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]))
    elif preprocess_config["preprocessing"]["text"]["language"] == "zh":
        # Procesamiento para chino
        phones = pinyin(text, style=Style.TONE3)
        phones = " ".join([p[0] for p in phones])
        sequence = np.array(text_to_sequence(phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]))
    else:
        raise ValueError(f"Idioma no soportado: {preprocess_config['preprocessing']['text']['language']}")
    
    return sequence

def synthesize_speech(text: str) -> Optional[str]:
    """
    Generates audio from text using FastSpeech2 with default model parameters.
    
    Args:
        text: Text to convert to speech
    
    Returns:
        Path to the generated audio file or None if it fails
    """
    try:
        print(f"Starting speech synthesis for text: {text}")
        
        # Preprocess text usando el mismo método que en synthesize.py
        if preprocess_config["preprocessing"]["text"]["language"] == "en":
            sequence = preprocess_english(text, preprocess_config)
        elif preprocess_config["preprocessing"]["text"]["language"] == "zh":
            sequence = preprocess_mandarin(text, preprocess_config)
        else:
            raise ValueError(f"Idioma no soportado: {preprocess_config['preprocessing']['text']['language']}")
        
        print(f"Preprocessed sequence length: {len(sequence)}")
        
        # Preparar batch como en synthesize.py
        ids = raw_texts = [text[:100]]
        speakers = np.array([0])  # speaker_id por defecto
        texts = np.array([sequence])
        text_lens = np.array([len(sequence)])
        batch = (ids, raw_texts, speakers, texts, text_lens, max(text_lens))
        
        # Convertir batch a device
        batch = to_device(batch, device)
        
        print("Generating mel spectrogram...")
        with torch.no_grad():
            # Forward pass con los mismos parámetros que en synthesize.py
            output = model(
                *(batch[2:]),
                p_control=1.0,  # pitch control
                e_control=1.0,  # energy control
                d_control=1.0   # duration control
            )
            
            # Crear directorio temporal para la síntesis
            temp_dir = tempfile.mkdtemp()
            print(f"Created temporary directory: {temp_dir}")
            
            # Usar synth_samples como en el código original
            synth_samples(
                batch,
                output,
                vocoder,
                model_config,
                preprocess_config,
                temp_dir
            )
            
            # Obtener el archivo generado
            output_filename = f"{ids[0]}.wav"
            temp_path = os.path.join(temp_dir, output_filename)
            
            # Mover el archivo a nuestro directorio de salida
            final_filename = f"{str(uuid.uuid4())}.wav"
            output_path = os.path.join(OUTPUT_DIR, final_filename)
            
            shutil.move(temp_path, output_path)
            
            # Limpiar directorio temporal
            shutil.rmtree(temp_dir)
            
            print(f"Audio generated successfully at: {output_path}")
            return output_path
        
    except Exception as e:
        print(f"Error during synthesis: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def preprocess_english(text, preprocess_config):
    """Implementación del preprocesamiento de inglés desde synthesize.py"""
    text = text.rstrip(punctuation)
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])

    # Diccionario mejorado de pronunciación
    simple_dict = {
        "hello": ["HH", "EH", "L", "OW"],
        "this": ["DH", "IH", "S"],
        "is": ["IH", "Z"],
        "a": ["AH"],
        "test": ["T", "EH", "S", "T"],
        "of": ["AH", "V"],
        "the": ["DH", "AH"],
        "fast": ["F", "AE", "S", "T"],
        "speech": ["S", "P", "IY", "CH"],
        "model": ["M", "AA", "D", "AH", "L"],
        "2": ["T", "UW"],
        "fastspeech": ["F", "AE", "S", "T", "S", "P", "IY", "CH"],
    }

    phones = []
    text = text.replace("FastSpeech 2", "fastspeech 2")
    words = re.split(r"([,;.\-\?\!\s+])", text)
    
    for w in words:
        w = w.lower().strip()
        if not w:
            continue
        if w in lexicon:
            phones += lexicon[w]
        elif w in simple_dict:
            phones += simple_dict[w]
        elif w in [",", ".", "!", "?"]:
            phones.append("sp")
        else:
            subwords = re.findall(r'[a-z]+|\d+', w)
            if subwords:
                for subw in subwords:
                    if subw in simple_dict:
                        phones += simple_dict[subw]
                    else:
                        phones.append("sp")
            else:
                phones.append("sp")
    
    phones = [p for p in phones if p]
    phones = "{" + "}{".join(phones) + "}"
    phones = re.sub(r"\{[^\w\s]?\}", "{sp}", phones)
    phones = re.sub(r"\{sp\}+", "{sp}", phones)
    phones = phones.replace("}{", " ")

    print("Raw Text Sequence: {}".format(text))
    print("Phoneme Sequence: {}".format(phones))
    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )

    return np.array(sequence)

def preprocess_mandarin(text, preprocess_config):
    """Implementación del preprocesamiento de mandarín desde synthesize.py"""
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])

    phones = []
    pinyins = [
        p[0]
        for p in pinyin(
            text, style=Style.TONE3, strict=False, neutral_tone_with_five=True
        )
    ]
    for p in pinyins:
        if p in lexicon:
            phones += lexicon[p]
        else:
            phones.append("sp")

    phones = "{" + " ".join(phones) + "}"
    print("Raw Text Sequence: {}".format(text))
    print("Phoneme Sequence: {}".format(phones))
    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )

    return np.array(sequence)

def read_lexicon(lex_path):
    """Función auxiliar para leer el léxico"""
    lexicon = {}
    with open(lex_path) as f:
        for line in f:
            temp = re.split(r"\s+", line.strip("\n"))
            word = temp[0]
            phones = temp[1:]
            if word.lower() not in lexicon:
                lexicon[word.lower()] = phones
    return lexicon