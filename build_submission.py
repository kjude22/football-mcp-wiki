import os
import zipfile

def main():
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Assignment_2")
    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Assignment_2.zip")
    
    if not os.path.exists(source_dir):
        print(f"Error: Submission directory not found at '{source_dir}'")
        return
        
    print("Packaging submission files...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, start=source_dir)
                zipf.write(file_path, relative_path)
                print(f" - Added: {relative_path}")
                
    print(f"Successfully built: {zip_path}")

if __name__ == "__main__":
    main()
