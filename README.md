# TTS Web App

Una aplicación web de Text-to-Speech (TTS) que utiliza FastSpeech2 para generar audio de alta calidad a partir de texto. Esta aplicación proporciona una interfaz web intuitiva para convertir texto a voz en tiempo real.

## 🚀 Características

- Conversión de texto a voz en tiempo real
- Soporte para inglés y mandarín
- Interfaz web moderna y fácil de usar
- API REST para integración con otros servicios
- Generación de audio de alta calidad usando FastSpeech2
- Vocoder HiFi-GAN para mejor calidad de audio

## 🛠️ Tecnologías Utilizadas

### Backend
- FastSpeech2 (basado en [ming024/FastSpeech2](https://github.com/ming024/FastSpeech2))
- FastAPI
- PyTorch
- HiFi-GAN vocoder
- Uvicorn

### Frontend
- React
- TypeScript
- Tailwind CSS
- Axios

## 📋 Prerrequisitos

- Python 3.8+
- Node.js 16+
- npm o yarn
- CUDA (opcional, pero recomendado para mejor rendimiento)

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/tts-web-app.git
cd tts-web-app
```

2. Instalar dependencias del backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Instalar dependencias del frontend:
```bash
cd frontend
npm install
# o
yarn install
```

4. Descargar los modelos preentrenados:
   - Descarga los checkpoints de FastSpeech2 y HiFi-GAN desde [ming024/FastSpeech2](https://github.com/ming024/FastSpeech2)
   - Coloca los archivos en `backend/output/ckpt/LJSpeech/`

## 🚀 Uso

1. Iniciar el backend:
```bash
cd backend
uvicorn main:app --reload --port 8001
```

2. Iniciar el frontend:
```bash
cd frontend
npm run dev
# o
yarn dev
```

3. Abrir el navegador en `http://localhost:5173`

## 📝 Uso de la API

### Endpoint de TTS
```http
POST /api/tts
Content-Type: application/json

{
    "text": "Texto a convertir en voz"
}
```

Respuesta:
```json
{
    "audio_path": "ruta/al/archivo/audio.wav"
}
```

## 🎯 Características Técnicas

- **Modelo TTS**: FastSpeech2 con las siguientes características:
  - Generación de mel-espectrogramas de alta calidad
  - Control de pitch, energía y duración
  - Soporte multi-speaker
  - Inferencia rápida

- **Vocoder**: HiFi-GAN
  - Generación de audio de alta fidelidad
  - Baja latencia
  - Calidad de audio superior

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Créditos

Este proyecto está basado en la implementación de FastSpeech2 por [ming024](https://github.com/ming024/FastSpeech2). Agradecemos su trabajo y contribución a la comunidad.

### Referencias
- [FastSpeech 2: Fast and High-Quality End-to-End Text to Speech](https://arxiv.org/abs/2006.04558)
- [HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis](https://arxiv.org/abs/2010.05646)

## 📧 Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter) - email@ejemplo.com

Link del Proyecto: [https://github.com/tu-usuario/tts-web-app](https://github.com/tu-usuario/tts-web-app)

## ⭐ Agradecimientos

- [ming024](https://github.com/ming024) por su implementación de FastSpeech2
- La comunidad de FastSpeech2 por su soporte y documentación
- Todos los contribuidores que han ayudado a mejorar este proyecto 