"""
Quick Dataset Creator
Helps create a minimal test dataset structure
"""

import os
import sys

def create_dataset_structure():
    """Create dataset folder structure"""
    
    print("\n" + "="*70)
    print("  VOICE DEEPFAKE DETECTOR - Dataset Structure Creator")
    print("="*70 + "\n")
    
    base_path = 'datasets'
    
    folders = [
        'datasets',
        'datasets/train',
        'datasets/train/real',
        'datasets/train/fake',
        'datasets/test',
        'datasets/test/real',
        'datasets/test/fake',
    ]
    
    print("Creating folder structure...\n")
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Created: {folder}")
    
    # Create README files in each folder
    readme_real = """# Real Voice Samples

Place REAL/AUTHENTIC voice recordings here.

## Examples:
- Voice recordings from real people
- Genuine phone calls
- Authentic interviews
- Real voice memos

## Sources:
- Record yourself speaking
- Mozilla Common Voice: https://commonvoice.mozilla.org/
- Free speech datasets
- Your own voice recordings

## Format:
- Supported: WAV, MP3, M4A, OGG, FLAC
- Duration: 1-30 seconds (optimal)
- Any sample rate (auto-converted to 16kHz)

## Naming:
- real_001.wav
- real_002.wav
- real_003.wav
- etc.
"""
    
    readme_fake = """# Fake/Synthetic Voice Samples

Place FAKE/SYNTHETIC/AI-GENERATED voice recordings here.

## Examples:
- AI-generated voices (ElevenLabs, Play.ht)
- Deepfake audio
- Voice clones
- Text-to-speech output
- Synthetic voices

## Sources:
1. **ElevenLabs** (https://elevenlabs.io/)
   - Generate AI voices
   - Download as MP3/WAV

2. **Play.ht** (https://play.ht/)
   - Text-to-speech
   - Download audio

3. **Murf.ai** (https://murf.ai/)
   - AI voice generation

## Format:
- Supported: WAV, MP3, M4A, OGG, FLAC
- Duration: 1-30 seconds (optimal)
- Any sample rate (auto-converted to 16kHz)

## Naming:
- fake_001.wav
- fake_002.wav
- fake_003.wav
- etc.
"""
    
    # Write README files
    with open('datasets/train/real/README.md', 'w') as f:
        f.write(readme_real)
    
    with open('datasets/train/fake/README.md', 'w') as f:
        f.write(readme_fake)
    
    with open('datasets/test/real/README.md', 'w') as f:
        f.write(readme_real.replace('Place REAL', 'Place TEST REAL'))
    
    with open('datasets/test/fake/README.md', 'w') as f:
        f.write(readme_fake.replace('Place FAKE', 'Place TEST FAKE'))
    
    print("\n" + "="*70)
    print("  FOLDER STRUCTURE CREATED SUCCESSFULLY!")
    print("="*70)
    
    print("\n📁 Dataset Structure:")
    print("""
    datasets/
    ├── train/
    │   ├── real/          ← Put REAL voice samples here
    │   └── fake/          ← Put FAKE voice samples here
    └── test/
        ├── real/          ← Put test REAL samples here (optional)
        └── fake/          ← Put test FAKE samples here (optional)
    """)
    
    print("\n📝 Next Steps:")
    print("1. Add audio files to datasets/train/real/ (at least 50 files)")
    print("2. Add audio files to datasets/train/fake/ (at least 50 files)")
    print("3. Run: python train.py")
    print("\n💡 See DATASET_GUIDE.md for detailed instructions")
    print("\n" + "="*70 + "\n")


def check_dataset():
    """Check if dataset has enough files"""
    
    print("\n" + "="*70)
    print("  DATASET CHECK")
    print("="*70 + "\n")
    
    paths = {
        'Training REAL': 'datasets/train/real',
        'Training FAKE': 'datasets/train/fake',
        'Test REAL': 'datasets/test/real',
        'Test FAKE': 'datasets/test/fake',
    }
    
    total_files = 0
    
    for name, path in paths.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) 
                    if f.endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac'))]
            count = len(files)
            total_files += count
            
            status = "✓" if count >= 10 else "⚠️"
            print(f"{status} {name:20s}: {count:3d} files")
        else:
            print(f"✗ {name:20s}: Folder not found")
    
    print("\n" + "-"*70)
    print(f"Total audio files: {total_files}")
    
    if total_files == 0:
        print("\n⚠️  No audio files found!")
        print("Please add audio files to datasets/train/real/ and datasets/train/fake/")
    elif total_files < 100:
        print("\n⚠️  Limited dataset!")
        print("Minimum recommended: 50 real + 50 fake = 100 files")
        print("For better accuracy, add more samples")
    else:
        print("\n✓ Dataset looks good!")
        print("Ready to train: python train.py")
    
    print("="*70 + "\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dataset Management Tool')
    parser.add_argument('--create', action='store_true', help='Create dataset folder structure')
    parser.add_argument('--check', action='store_true', help='Check dataset status')
    
    args = parser.parse_args()
    
    if args.create or (not args.check):
        create_dataset_structure()
    
    if args.check:
        check_dataset()
    elif os.path.exists('datasets'):
        check_dataset()
