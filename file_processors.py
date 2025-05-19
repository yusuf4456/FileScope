import os
import threading
from queue import Queue
from metadata_extractors import extract_metadata


class BatchProcessor:

    def __init__(self, callback=None, max_workers=4):
        self.queue = Queue()
        self.results = {}
        self.processed_count = 0
        self.total_count = 0
        self.active = False
        self.callback = callback
        self.workers = []
        self.max_workers = max_workers
        self.lock = threading.Lock()

    def add_files(self, file_paths):
        with self.lock:
            for path in file_paths:
                if os.path.isfile(path):
                    self.queue.put(path)
                    self.total_count += 1

    def start(self):
        if self.active:
            return

        self.active = True
        self.processed_count = 0
        self.results = {}

        # Create and start worker threads
        for _ in range(min(self.max_workers, self.total_count)):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker(self):
        while self.active:
            try:
                # Get file from queue with timeout to check active flag periodically
                path = self.queue.get(timeout=0.5)

                # Process the file
                metadata = extract_metadata(path)

                # Store the result
                with self.lock:
                    self.results[path] = metadata
                    self.processed_count += 1

                    # Call the callback with progress information
                    if self.callback:
                        progress = (self.processed_count / self.total_count) * 100
                        self.callback(progress, self.processed_count, self.total_count)

                # Mark task as done
                self.queue.task_done()

                # Check if all files have been processed
                if self.processed_count >= self.total_count:
                    self.active = False

                    # Final callback
                    if self.callback:
                        self.callback(100, self.processed_count, self.total_count, finished=True)

            except Queue.Empty:
                # Queue is empty, continue the loop
                pass

            except Exception as e:
                print(f"Error in worker thread: {e}")
                with self.lock:
                    self.processed_count += 1
                self.queue.task_done()

    def stop(self):
        self.active = False

        # Wait for all worker threads to finish
        for worker in self.workers:
            if worker.is_alive():
                worker.join(1.0)  # Wait with timeout

        self.workers = []

    def get_results(self):
        return self.results

    def clear(self):
        self.stop()
        with self.lock:
            self.queue = Queue()
            self.results = {}
            self.processed_count = 0
            self.total_count = 0


class FileRemover:

    @staticmethod
    def remove_metadata(file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext in ['.jpg', '.jpeg', '.png', '.tiff', '.webp']:
                # Use PIL to strip metadata from image
                from PIL import Image

                # Open the image and get its data
                with Image.open(file_path) as img:
                    # Convert to RGB if RGBA (for PNG)
                    if img.mode == 'RGBA' and ext != '.png':
                        img = img.convert('RGB')

                    # Create a new image with the same data but no metadata
                    data = list(img.getdata())
                    new_img = Image.new(img.mode, img.size)
                    new_img.putdata(data)

                    # Generate new filename
                    base, extension = os.path.splitext(file_path)
                    new_path = f"{base}_no_metadata{extension}"

                    # Save without metadata
                    new_img.save(new_path)

                return new_path

            elif ext in ['.mp3', '.m4a', '.flac', '.ogg']:
                # For audio files, need mutagen
                try:
                    import mutagen

                    # Generate new filename
                    base, extension = os.path.splitext(file_path)
                    new_path = f"{base}_no_metadata{extension}"

                    # Copy the file
                    import shutil
                    shutil.copy2(file_path, new_path)

                    # Remove tags
                    audio = mutagen.File(new_path)
                    if audio is not None:
                        audio.delete()
                        audio.save()

                    return new_path
                except ImportError:
                    return "Error: Mutagen library not available for audio metadata removal"

            else:
                return "Unsupported file type for metadata removal"

        except Exception as e:
            return f"Error removing metadata: {str(e)}"


class FileComparer:

    @staticmethod
    def compare(file_path1, file_path2):
        try:
            # Extract metadata from both files
            metadata1 = extract_metadata(file_path1)
            metadata2 = extract_metadata(file_path2)

            # Get common keys for comparison
            common_keys = set(metadata1.keys()) & set(metadata2.keys())

            # Compare values
            differences = {}
            similarities = {}

            for key in common_keys:
                if metadata1[key] != metadata2[key]:
                    differences[key] = {
                        "file1": metadata1[key],
                        "file2": metadata2[key]
                    }
                else:
                    similarities[key] = metadata1[key]

            # Find keys unique to each file
            only_in_file1 = {}
            for key in set(metadata1.keys()) - common_keys:
                only_in_file1[key] = metadata1[key]

            only_in_file2 = {}
            for key in set(metadata2.keys()) - common_keys:
                only_in_file2[key] = metadata2[key]

            # Return comparison results
            return {
                "differences": differences,
                "similarities": similarities,
                "only_in_file1": only_in_file1,
                "only_in_file2": only_in_file2,
                "file1": os.path.basename(file_path1),
                "file2": os.path.basename(file_path2)
            }

        except Exception as e:
            return {"error": str(e)}


class FileFilter:

    @staticmethod
    def filter_files(files_metadata, criteria):
        """
        Filter files based on metadata criteria

        Args:
            files_metadata: Dictionary with file paths as keys and metadata as values
            criteria: List of criteria dictionaries with fields:
                - field: Metadata field name
                - operator: '==', '!=', '>', '<', 'contains', 'starts_with', 'ends_with'
                - value: Value to compare against

        Returns:
            Dictionary of filtered file paths and their metadata
        """
        result = {}

        for file_path, metadata in files_metadata.items():
            if FileFilter._matches_criteria(metadata, criteria):
                result[file_path] = metadata

        return result

    @staticmethod
    def _matches_criteria(metadata, criteria_list):
        for criteria in criteria_list:
            field = criteria.get('field')
            operator = criteria.get('operator')
            value = criteria.get('value')

            if not field or not operator:
                continue

            if field not in metadata:
                return False

            field_value = metadata[field]

            try:
                if isinstance(value, str) and isinstance(field_value, str):
                    # String comparison
                    if operator == '==':
                        if field_value != value:
                            return False
                    elif operator == '!=':
                        if field_value == value:
                            return False
                    elif operator == 'contains':
                        if value.lower() not in field_value.lower():
                            return False
                    elif operator == 'starts_with':
                        if not field_value.lower().startswith(value.lower()):
                            return False
                    elif operator == 'ends_with':
                        if not field_value.lower().endswith(value.lower()):
                            return False
                else:
                    num_field_value = float(field_value) if isinstance(field_value, (int, float, str)) else 0
                    num_value = float(value) if isinstance(value, (int, float, str)) else 0

                    if operator == '==':
                        if num_field_value != num_value:
                            return False
                    elif operator == '!=':
                        if num_field_value == num_value:
                            return False
                    elif operator == '>':
                        if num_field_value <= num_value:
                            return False
                    elif operator == '<':
                        if num_field_value >= num_value:
                            return False
                    elif operator == '>=':
                        if num_field_value < num_value:
                            return False
                    elif operator == '<=':
                        if num_field_value > num_value:
                            return False
            except (ValueError, TypeError):
                return False

        return True
