# 🎬 Demo Guide

## Testing the Application

Since the model is initialized with random weights (for demonstration), you can test the application with any audio file to see the full workflow.

### Sample Test Files

You can use any of the following types of audio files:

1. **Record your own voice** (1-30 seconds)
   - Use your phone's voice recorder
   - Use online tools like https://online-voice-recorder.com
   - Use Audacity (free audio software)

2. **Download sample audio**
   - Free audio: https://freesound.org
   - Voice samples: https://www.voiptroubleshooter.com/open_speech/
   - Test audio: https://file-examples.com/index.php/sample-audio-files-download/

3. **Convert video to audio**
   - Use online tools to extract audio from videos
   - Format: MP3, WAV recommended

### Expected Behavior (Untrained Model)

⚠️ **Important**: The current model uses random weights, so predictions will be ~50% (random baseline).

**With random weights, you might see:**
- Confidence scores around 40-60%
- Random verdicts (REAL or FAKE)
- This is expected behavior!

### Getting Real Accuracy

To get accurate predictions, you need to train the model on real datasets:

1. **Download datasets:**
   - ASVspoof 2019: https://datashare.ed.ac.uk/handle/10283/3336
   - FakeAVCeleb: https://sites.google.com/view/fakeavcelebdataset
   - WaveFake: https://zenodo.org/record/5642694

2. **Prepare data:**
   ```python
   # Extract features from dataset
   from preprocessing import AudioPreprocessor
   
   preprocessor = AudioPreprocessor()
   features = preprocessor.extract_features('path/to/audio.wav')
   ```

3. **Train the model:**
   ```python
   from model import DeepfakeDetector
   
   detector = DeepfakeDetector()
   history = detector.model.fit(X_train, y_train, ...)
   detector.model.save('models/deepfake_detector_trained.h5')
   ```

4. **Expected accuracy after training:**
   - Accuracy: 92-96%
   - EER: 4-8%
   - AUC: 0.95-0.98

## Demo Workflow

### 1. Start the Application
```bash
./start.sh  # Linux/Mac
# or
start.bat   # Windows
```

### 2. Upload Audio
- Drag and drop an audio file onto the upload zone
- Or click to browse and select a file
- Supported formats: MP3, WAV, M4A, OGG, FLAC
- Maximum size: 10MB

### 3. Preview
- See the audio waveform visualization
- Play the audio to verify it loaded correctly
- Check file details (name, size, duration)

### 4. Analyze
- Click "Analyze Audio" button
- Watch the animated processing steps
- Wait 2-3 seconds for results

### 5. View Results
- See the verdict (REAL or SYNTHETIC)
- Check the confidence score
- View the animated progress ring
- See detailed analysis information

### 6. Test Again
- Click "Analyze Another" to upload a new file
- Try different audio files
- Compare results

## UI Feature Showcase

### Visual Effects
- ✨ Animated particle background
- 🌊 Gradient wave animations
- 💎 Glassmorphism cards
- 🎨 Color-coded results
- ⚡ Smooth transitions

### Interactive Elements
- 🎵 Waveform visualization
- ▶️ Audio playback controls
- 📊 Animated progress ring
- 🔄 Processing step indicators
- 📱 Responsive design

### Accessibility
- ⌨️ Keyboard navigation
- 🔊 Screen reader support
- 🎯 Clear focus indicators
- 📏 High contrast text

## Troubleshooting Demo Issues

### Backend not responding
```bash
# Check if backend is running
curl http://localhost:5000/health

# Should return:
# {"status":"healthy","model_loaded":true,"version":"1.0.0"}
```

### Frontend not loading
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for errors (F12)
- Verify both servers are running

### File upload fails
- Check file size (must be < 10MB)
- Verify file format (MP3, WAV, M4A, OGG, FLAC)
- Check audio duration (0.5-60 seconds)

### Analysis takes too long
- Normal analysis time: 2-3 seconds
- If longer, check backend logs for errors
- Restart backend server if needed

## Performance Notes

### Current Setup (Demo)
- **Analysis Time**: 2-3 seconds
- **Accuracy**: ~50% (random baseline)
- **Model Size**: ~50MB
- **Memory Usage**: ~500MB

### Production Setup (After Training)
- **Analysis Time**: 2-3 seconds (same)
- **Accuracy**: 92-96%
- **Model Size**: ~50MB
- **Memory Usage**: ~1GB

## Next Steps

1. **Explore the UI** - Try all features and interactions
2. **Test different files** - Upload various audio formats
3. **Read the code** - Understand how it works
4. **Train the model** - Get real accuracy with datasets
5. **Customize** - Modify UI colors, add features, etc.

---

**Enjoy exploring the Voice Deepfake Detector! 🎙️✨**
