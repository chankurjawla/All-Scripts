import os
import shutil
from pathlib import Path

def copy_updated_files(src_dir, dst_dir):
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)

    # Walk through source directory
    for root, dirs, files in os.walk(src_dir):
        root_path = Path(root)
        # Determine relative path from source directory
        relative_path = root_path.relative_to(src_dir)
        # Create destination path for subfolders
        dest_subdir = dst_dir / relative_path
        if not dest_subdir.exists():
            dest_subdir.mkdir(parents=True, exist_ok=True)

        for file in files:
            src_file = root_path / file
            dest_file = dest_subdir / file

            # If file not in destination or updated, copy it
            if (not dest_file.exists() or
                src_file.stat().st_mtime > dest_file.stat().st_mtime):
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {src_file}")
#Folder in HDD for backup
FullBackup = "/srv/dev-disk-by-uuid-b5909f69-78a7-466f-9006-250ddf83dce0"
#Folders in SSD to be backed up
MediaStorage ="/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/MediaStorage"
NAS = "/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/NAS"
GooglePhoto = "/srv/dev-disk-by-uuid-f0425cc4-37bf-4419-b75f-867d4bb647ca/GooglePhotos"
GooglePhototemp = "/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/NAS/2_Images/GooglePhotos"
if __name__ == "__main__":
    #source_folder ="/srv/dev-disk-by-uuid-b5909f69-78a7-466f-9006-250ddf83dce0/FullBackup"
    #destination_folder ="/srv/dev-disk-by-uuid-b5909f69-78a7-466f-9006-250ddf83dce0"
    #source_folder = "/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2"
    copy_updated_files(NAS,FullBackup)
    copy_updated_files(MediaStorage,FullBackup)
    copy_updated_files(GooglePhototemp,GooglePhoto)
