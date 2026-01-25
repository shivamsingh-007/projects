# 📚 Dataset Preparation & Training Guide

## 🎯 Complete Training Workflow

### Step 1: Create Dataset Folders

Run these commands in your project directory:

```cmd
cd C:\Users\shiva\Documents\projects\voice-deepfake-detector

mkdir datasets
mkdir datasets\train
mkdir datasets\train\real
mkdir datasets\train\fake
mkdir datasets\test
mkdir datasets\test\real
mkdir datasets\test\fake
```

**Folder Structure:**
```
voice-deepfake-detector/
│
├── datasets/               # Create this!
│   ├── train/             # Training data
│   │   ├── real/          # Real voice samples
│   │   └── fake/          # Fake/synthetic samples
│   └── test/              # Test data (optional)
│       ├── real/
│       └── fake/
```

---

## 📥 Step 2: Get Dataset Files

### Option A: Download Public Datasets

#### **ASVspoof 2019** (Recommended) ⭐

1. **Download:**
   - Visit: https://datashare.ed.ac.uk/handle/10283/3336
   - Download: LA (Logical Access) subset (~7GB)
   - Extract the ZIP file

2. **Copy files:**
   ```
   ASVspoof2019_LA_train/flac/
   ├── LA_T_1000265.flac → Copy to datasets/train/real/
   ├── LA_T_1000266.flac → Copy to datasets/train/fake/
   └── ...
   ```

3. **Check the protocol file:**
   - Open `ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt`
   - Format: `speaker file_id - attack_type label`
   - `bonafide` = REAL → Copy to `real/`
   - `spoof` = FAKE → Copy to `fake/`

#### **FakeAVCeleb** (Celebrity Voices)

1. **Download:** https://sites.google.com/view/fakeavcelebdataset
2. **Extract audio** from videos using:
   ```cmd
   # Install ffmpeg first: https://ffmpeg.org/download.html
   ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav
   ```

#### **WaveFake** (Various Generators)

1. **Download:** https://zenodo.org/record/5642694
2. Already organized in real/fake folders!
3. Just copy to your `datasets/` folder

---

### Option B: Create Your Own Dataset

If you can't download large datasets, create a small test dataset:

#### **Collect Real Voices** (50-100 samples):
- Record yourself speaking (10-30 seconds each)
- Download from: https://commonvoice.mozilla.org/
- Use voice memos from friends/family
- Download from: https://www.voiptroubleshooter.com/open_speech/

**Save as:** `datasets/train/real/real_001.wav`, `real_002.wav`, etc.

#### **Collect Fake Voices** (50-100 samples):

Use these free AI voice generators:

1. **ElevenLabs** (https://elevenlabs.io/)
   - Generate AI voices
   - Download as MP3/WAV

2. **Play.ht** (https://play.ht/)
   - Text-to-speech
   - Download audio

3. **Murf.ai** (https://murf.ai/)
   - AI voice generation
   - Free trial available

**Save as:** `datasets/train/fake/fake_001.wav`, `fake_002.wav`, etc.

---

## 🎵 Step 3: Prepare Audio Files

### File Requirements:
- ✅ **Formats:** WAV, MP3, M4A, OGG, FLAC
- ✅ **Duration:** 1-30 seconds (optimal)
- ✅ **Sample Rate:** Any (auto-converted to 16kHz)
- ✅ **Channels:** Mono or Stereo (auto-converted to mono)

### Batch Convert (if needed):

**Using ffmpeg:**
```cmd
# Convert all files in a folder to WAV
for %i in (*.mp3) do ffmpeg -i "%i" -ar 16000 -ac 1 "%~ni.wav"
```

**Using Audacity** (Free software):
1. Download: https://www.audacityteam.org/
2. File → Open → Select audio
3. Tracks → Resample → 16000 Hz
4. File → Export → Export as WAV

---

## 🚀 Step 4: Train the Model

### Install Training Dependencies

```cmd
cd C:\Users\shiva\Documents\projects\voice-deepfake-detector
venv\Scripts\activate
pip install tqdm scikit-learn
```

### Run Training Script

```cmd
python train.py
```

**Training Output:**
```
====================================================================
  VOICE DEEPFAKE DETECTOR - TRAINING
====================================================================

Loading REAL samples...
Loading real: 100%|████████████████| 150/150 [00:45<00:00]

Loading FAKE samples...
Loading fake: 100%|████████████████| 150/150 [00:45<00:00]

Dataset loaded: 300 samples
  REAL: 150 samples
  FAKE: 150 samples

TRAINING MODEL...
[Random Forest Training...]

EVALUATING MODEL...
Accuracy: 89.50%

Classification Report:
              precision    recall  f1-score   support
      FAKE       0.88      0.90      0.89        30
      REAL       0.91      0.89      0.90        30
  
✓ Model saved to: models/deepfake_detector_lite.pkl

====================================================================
  TRAINING COMPLETE!
  Accuracy: 89.50%
  Model ready to use in the application
====================================================================
```

---

## 📊 Step 5: Test Trained Model

### Restart Backend with Trained Model

```cmd
cd backend
python app.py
```

**You should see:**
```
INFO:model_lite:Loading model from ../models/deepfake_detector_lite.pkl
INFO:model_lite:Model loaded successfully
INFO:__main__:Model loaded: True
```

### Test with Real Audio

1. Go to: http://localhost:3000
2. Upload an audio file
3. Click "Analyze Audio"
4. **Now you'll get accurate predictions!** 🎉

---

## 💡 Tips for Better Accuracy

### 1. **More Data = Better Model**
- Minimum: 50 real + 50 fake (for testing)
- Good: 500 real + 500 fake
- Best: 5000+ real + 5000+ fake

### 2. **Balanced Dataset**
- Same number of real and fake samples
- Similar duration distribution
- Similar quality/format

### 3. **Diverse Data**
- Multiple speakers
- Different languages
- Various recording conditions
- Different deepfake methods

### 4. **Data Augmentation**

Add variations to existing samples:

```python
from preprocessing import AudioPreprocessor

preprocessor = AudioPreprocessor()

# Load audio
audio, sr = preprocessor.load_audio('sample.wav')

# Add noise
noisy = preprocessor.augment_audio(audio)

# Save augmented version
import soundfile as sf
sf.write('sample_augmented.wav', noisy, sr)
```

---

## 🔍 Verify Dataset is Ready

Before training, check:

```cmd
# Count files
dir datasets\train\real /b | find /c /v ""
dir datasets\train\fake /b | find /c /v ""

# Should show number of files in each folder
```

**Minimum recommended:**
- Real: 50 files
- Fake: 50 files

**Optimal:**
- Real: 500+ files
- Fake: 500+ files

---

## 🎯 Quick Start: Minimal Dataset

**For testing (15 minutes):**

1. **Record 10 voice memos** on your phone (10 seconds each)
   - Save to: `datasets/train/real/`

2. **Generate 10 AI voices:**
   - Go to: https://elevenlabs.io/
   - Type 10 different sentences
   - Download each as MP3
   - Save to: `datasets/train/fake/`

3. **Train:**
   ```cmd
   python train.py
   ```

4. **Test in app!**

---

## ❓ Troubleshooting

### "No training data found"
- Check folder structure is correct
- Ensure files have audio extensions (.wav, .mp3, etc.)
- Verify files aren't corrupted

### "Error processing file"
- File might be corrupted
- Try converting with Audacity first
- Check if file is actually audio

### "Not enough memory"
- Reduce dataset size
- Process in batches
- Close other programs

---

## 📈 Expected Results

| Dataset Size | Training Time | Expected Accuracy |
|-------------|--------------|-------------------|
| 100 samples | 2-5 minutes | 70-80% |
| 500 samples | 10-20 minutes | 80-90% |
| 1000 samples | 20-40 minutes | 85-92% |
| 5000+ samples | 1-2 hours | 90-95% |

---

**Ready to train? Let's make your detector actually work!** 🚀
