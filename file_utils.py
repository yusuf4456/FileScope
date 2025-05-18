import os
import hashlib
import datetime
import magic
import json
import csv
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from constants import FILE_TYPES


def get_file_extension(file_path):
    return os.path.splitext(file_path)[1].lower()


def get_file_type_category(file_path):
    ext = get_file_extension(file_path)

    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category

    return "Other"


def calculate_checksum(file_path, algorithm='md5'):
    try:
        hasher = None
        if algorithm.lower() == 'md5':
            hasher = hashlib.md5()
        elif algorithm.lower() == 'sha1':
            hasher = hashlib.sha1()
        elif algorithm.lower() == 'sha256':
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        with open(file_path, 'rb') as f:
            # Read and update hash in chunks to avoid memory issues with large files
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        return hasher.hexdigest()
    except Exception as e:
        print(f"Error calculating checksum: {e}")
        return "Checksum calculation failed"


def get_file_mime_type(file_path):
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except:
        return "application/octet-stream"


def get_file_info(file_path):
    try:
        stat = os.stat(file_path)
        file_info = {
            'File Name': os.path.basename(file_path),
            'File Path': os.path.abspath(file_path),
            'File Size': stat.st_size,
            'File Size (Formatted)': format_file_size(stat.st_size),
            'Creation Date': format_timestamp(stat.st_ctime),
            'Modified Date': format_timestamp(stat.st_mtime),
            'Accessed Date': format_timestamp(stat.st_atime),
            'File Extension': get_file_extension(file_path),
            'File Type Category': get_file_type_category(file_path),
            'MIME Type': get_file_mime_type(file_path),
        }
        return file_info
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {}


def format_timestamp(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def export_metadata_to_file(metadata, file_path, format_type):
    try:
        if format_type == '.json':
            with open(file_path, 'w') as f:
                json.dump(metadata, f, indent=4)

        elif format_type == '.csv':
            with open(file_path, 'w', newline='') as f:
                if isinstance(metadata, list):
                    if metadata:
                        fieldnames = set()
                        for meta in metadata:
                            fieldnames.update(meta.keys())

                        writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                        writer.writeheader()
                        for meta in metadata:
                            writer.writerow(meta)
                else:
                    writer = csv.DictWriter(f, fieldnames=sorted(metadata.keys()))
                    writer.writeheader()
                    writer.writerow(metadata)

        elif format_type == '.xml':
            if isinstance(metadata, list):
                root = ET.Element("Metadata_Collection")
                for idx, meta in enumerate(metadata):
                    file_elem = ET.SubElement(root, "File", id=str(idx + 1))
                    for key, value in meta.items():
                        elem = ET.SubElement(file_elem, key.replace(" ", "_"))
                        elem.text = str(value)
            else:
                root = ET.Element("Metadata")
                for key, value in metadata.items():
                    elem = ET.SubElement(root, key.replace(" ", "_"))
                    elem.text = str(value)

            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            with open(file_path, 'w') as f:
                f.write(reparsed.toprettyxml(indent="  "))

        elif format_type == '.html':
            with open(file_path, 'w') as f:
                f.write("<!DOCTYPE html>\n<html>\n<head>\n")
                f.write("<title>Metadata Report</title>\n")
                f.write("<style>\n")
                f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
                f.write("table { border-collapse: collapse; width: 100%; }\n")
                f.write("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
                f.write("th { background-color: #f2f2f2; }\n")
                f.write("tr:nth-child(even) { background-color: #f9f9f9; }\n")
                f.write("h1 { color: #333; }\n")
                f.write("</style>\n</head>\n<body>\n")

                f.write(f"<h1>Metadata Report: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>\n")

                if isinstance(metadata, list):
                    for idx, meta in enumerate(metadata):
                        file_name = meta.get('File Name', f"File {idx + 1}")
                        f.write(f"<h2>{file_name}</h2>\n")
                        f.write("<table>\n<tr><th>Property</th><th>Value</th></tr>\n")
                        for key, value in sorted(meta.items()):
                            f.write(f"<tr><td>{key}</td><td>{value}</td></tr>\n")
                        f.write("</table>\n<br>\n")
                else:
                    f.write("<table>\n<tr><th>Property</th><th>Value</th></tr>\n")
                    for key, value in sorted(metadata.items()):
                        f.write(f"<tr><td>{key}</td><td>{value}</td></tr>\n")
                    f.write("</table>\n")

                f.write("</body>\n</html>")

        else:
            with open(file_path, 'w') as f:
                if isinstance(metadata, list):
                    for idx, meta in enumerate(metadata):
                        f.write(f"===== File {idx + 1} =====\n")
                        for key, value in sorted(meta.items()):
                            f.write(f"{key}: {value}\n")
                        f.write("\n")
                else:
                    # For single file metadata
                    for key, value in sorted(metadata.items()):
                        f.write(f"{key}: {value}\n")

        return True
    except Exception as e:
        print(f"Error exporting metadata: {e}")
        return False


def compare_metadata(metadata1, metadata2):
    diff = {}
    all_keys = set(metadata1.keys()) | set(metadata2.keys())

    for key in all_keys:
        if key not in metadata1:
            diff[key] = {"file1": "N/A", "file2": metadata2[key], "status": "Missing in File 1"}
        elif key not in metadata2:
            diff[key] = {"file1": metadata1[key], "file2": "N/A", "status": "Missing in File 2"}
        elif metadata1[key] != metadata2[key]:
            diff[key] = {"file1": metadata1[key], "file2": metadata2[key], "status": "Different"}

    return diff
