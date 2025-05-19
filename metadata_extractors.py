import os
import exifread
import hashlib
import datetime
import mimetypes
from PIL import Image
import file_utils

try:
    import magic

    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

try:
    import mutagen

    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

try:
    import PyPDF2

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


def extract_metadata(file_path, calc_checksums=True):
    if not os.path.exists(file_path):
        return {"Error": "File does not exist"}

    metadata = file_utils.get_file_info(file_path)

    if calc_checksums:
        metadata['Checksum (MD5)'] = file_utils.calculate_checksum(file_path, 'md5')
        metadata['Checksum (SHA1)'] = file_utils.calculate_checksum(file_path, 'sha1')
        metadata['Checksum (SHA256)'] = file_utils.calculate_checksum(file_path, 'sha256')


    file_type = file_utils.get_file_type_category(file_path)

    if file_type == "Images":
        image_metadata = extract_image_metadata(file_path)
        metadata.update(image_metadata)
    elif file_type == "Audio" and HAS_MUTAGEN:
        audio_metadata = extract_audio_metadata(file_path)
        metadata.update(audio_metadata)
    elif file_type == "Video":
        video_metadata = extract_video_metadata(file_path)
        metadata.update(video_metadata)
    elif file_type == "Documents":
        doc_metadata = extract_document_metadata(file_path)
        metadata.update(doc_metadata)

    return metadata


def extract_image_metadata(file_path):
    metadata = {}

    try:
        with open(file_path, 'rb') as image_file:
            tags = exifread.process_file(image_file)

            for tag, value in tags.items():
                if tag.startswith('JPEGThumbnail'):
                    continue
                metadata[f"EXIF: {tag}"] = str(value)

            metadata['Date and Time'] = str(
                tags.get('EXIF DateTimeOriginal', tags.get('Image DateTime', 'Not Available')))
            metadata['Camera Model'] = str(tags.get('Image Model', 'Not Available'))
            metadata['Camera Make'] = str(tags.get('Image Make', 'Not Available'))
            metadata['Software'] = str(tags.get('Image Software', 'Not Available'))
            metadata['GPS Coordinates'] = get_gps_coordinates(tags)
            metadata['Exposure Time'] = str(tags.get('EXIF ExposureTime', 'Not Available'))
            metadata['F-Stop'] = str(tags.get('EXIF FNumber', 'Not Available'))
            metadata['ISO Speed'] = str(tags.get('EXIF ISOSpeedRatings', 'Not Available'))
            metadata['Focal Length'] = str(tags.get('EXIF FocalLength', 'Not Available'))
    except Exception as e:
        metadata['EXIF Data'] = f"Error extracting EXIF data: {e}"

    try:
        with Image.open(file_path) as img:
            metadata['Image Format'] = img.format
            metadata['Image Mode'] = img.mode
            metadata['Image Width'] = img.width
            metadata['Image Height'] = img.height
            metadata['Image Size'] = f"{img.width}x{img.height}"
            metadata['Megapixels'] = round((img.width * img.height) / 1e6, 2)

            for key, value in img.info.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[f"Image Info: {key}"] = value
    except Exception as e:
        metadata['Image Data'] = f"Error extracting image data: {e}"

    return metadata


def get_gps_coordinates(exif_data):
    if 'GPS GPSLatitude' in exif_data and 'GPS GPSLongitude' in exif_data:
        try:
            lat = convert_to_degrees(exif_data['GPS GPSLatitude'].values)
            lon = convert_to_degrees(exif_data['GPS GPSLongitude'].values)

            if 'GPS GPSLatitudeRef' in exif_data and exif_data['GPS GPSLatitudeRef'].values[0] != 'N':
                lat = -lat
            if 'GPS GPSLongitudeRef' in exif_data and exif_data['GPS GPSLongitudeRef'].values[0] != 'E':
                lon = -lon

            return f"{lat:.6f}, {lon:.6f}"
        except Exception as e:
            return f"Error parsing GPS data: {e}"
    return "Not Available"


def convert_to_degrees(value):
    d = float(value[0].num) / float(value[0].den)
    m = float(value[1].num) / float(value[1].den)
    s = float(value[2].num) / float(value[2].den)
    return d + (m / 60.0) + (s / 3600.0)


def extract_audio_metadata(file_path):
    metadata = {}

    if not HAS_MUTAGEN:
        metadata['Audio Data'] = "Mutagen library not available for audio metadata extraction"
        return metadata

    try:
        audio = mutagen.File(file_path)
        if audio is not None:
            if hasattr(audio.info, 'length'):
                metadata['Duration'] = format_duration(audio.info.length)
            if hasattr(audio.info, 'bitrate'):
                metadata['Bitrate'] = f"{audio.info.bitrate / 1000:.0f} kbps"
            if hasattr(audio.info, 'sample_rate'):
                metadata['Sample Rate'] = f"{audio.info.sample_rate} Hz"
            if hasattr(audio.info, 'channels'):
                metadata['Channels'] = audio.info.channels

            for key, value in audio.items():
                if isinstance(value, list) and len(value) == 1:
                    metadata[f"Tag: {key}"] = str(value[0])
                else:
                    metadata[f"Tag: {key}"] = str(value)

            common_tags = {
                'title': ['title', 'TIT2'],
                'artist': ['artist', 'TPE1', 'performer'],
                'album': ['album', 'TALB'],
                'date': ['date', 'year', 'TDRC'],
                'genre': ['genre', 'TCON'],
                'track': ['tracknumber', 'track', 'TRCK'],
                'composer': ['composer', 'TCOM'],
            }

            for friendly_name, possible_tags in common_tags.items():
                for tag in possible_tags:
                    if tag in audio:
                        value = audio[tag]
                        if isinstance(value, list) and len(value) == 1:
                            metadata[friendly_name.title()] = str(value[0])
                        else:
                            metadata[friendly_name.title()] = str(value)
                        break
    except Exception as e:
        metadata['Audio Data'] = f"Error extracting audio metadata: {e}"

    return metadata


def format_duration(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    else:
        return f"{m}:{s:02d}"


def extract_video_metadata(file_path):
    metadata = {}

    # Basic video metadata - without additional libraries
    # In a more comprehensive implementation, you might want to use libraries like
    # moviepy, ffmpeg-python, or python-ffmpeg to extract more detailed information

    # For now, we'll just identify it as a video file
    metadata['Media Type'] = "Video"

    if HAS_MAGIC:
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(file_path)
            metadata['MIME Type'] = mime_type

            magic_desc = magic.Magic()
            desc = magic_desc.from_file(file_path)
            metadata['File Description'] = desc

            if 'x' in desc and 'resolution' in desc:
                resolution_part = desc.split('resolution')[1].split(',')[0]
                metadata['Resolution'] = resolution_part.strip()
        except Exception as e:
            metadata['Magic Error'] = str(e)

    return metadata


def extract_document_metadata(file_path):
    metadata = {}
    ext = file_utils.get_file_extension(file_path)

    if ext == '.pdf' and HAS_PYPDF2:
        try:
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfFileReader(f)
                metadata['Page Count'] = pdf.getNumPages()

                info = pdf.getDocumentInfo()
                if info:
                    for key, value in info.items():
                        if key.startswith('/'):
                            key = key[1:]
                        metadata[f"PDF: {key}"] = str(value)

                metadata['PDF Version'] = pdf.pdf_header
        except Exception as e:
            metadata['PDF Data'] = f"Error extracting PDF metadata: {e}"

    elif ext in ['.txt', '.csv', '.log']:
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                words = content.split()

                metadata['Line Count'] = len(lines)
                metadata['Word Count'] = len(words)
                metadata['Character Count'] = len(content)
        except Exception as e:
            metadata['Text Analysis'] = f"Error analyzing text: {e}"

    return metadata
