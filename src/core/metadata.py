import os
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PyQt6.QtGui import QImage

def extract_metadata(file_path):
    metadata = {
        'title': os.path.splitext(os.path.basename(file_path))[0],
        'artist': 'Unknown Artist',
        'cover_art': None
    }

    if file_path.lower().endswith(('.gif', '.jpg', '.png', '.jpeg', '.bmp')):
        return metadata

    try:
        audio = File(file_path)
        if not audio:
            return metadata

        if 'TIT2' in audio:
            metadata['title'] = str(audio['TIT2'])
        elif 'title' in audio and len(audio['title']) > 0:
            metadata['title'] = str(audio['title'][0])

        if 'TPE1' in audio:
            metadata['artist'] = str(audio['TPE1'])
        elif 'artist' in audio and len(audio['artist']) > 0:
            metadata['artist'] = str(audio['artist'][0])

        image = None

        if isinstance(audio, MP3) or isinstance(audio, ID3):
             if not isinstance(audio, ID3):
                 try:
                     audio = ID3(file_path)
                 except:
                     pass

             if audio:
                 for key in audio.keys():
                     if key.startswith('APIC'):
                         apic = audio[key]
                         img_data = apic.data
                         image = QImage.fromData(img_data)
                         break

        elif hasattr(audio, 'pictures') and audio.pictures:
             p = audio.pictures[0]
             image = QImage.fromData(p.data)

        elif 'covr' in audio:
             if len(audio['covr']) > 0:
                 img_data = audio['covr'][0]
                 image = QImage.fromData(img_data)

        if image and not image.isNull():
            metadata['cover_art'] = image

    except Exception as e:
        print(f"Error extracting metadata for {file_path}: {e}")

    return metadata
