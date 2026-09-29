import kagglehub
import shutil
import os

print("Downloading dataset...")
path = kagglehub.dataset_download("unseemlycoder/smart-energy-meters-in-bangalore-india")
print(f"Downloaded to {path}")

# copy contents to data/raw
target_dir = r"c:\Users\Admin\OneDrive\Desktop\energy consumption\energy-consumption-prediction\backend\data\raw"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

for file in os.listdir(path):
    source = os.path.join(path, file)
    destination = os.path.join(target_dir, file)
    if os.path.isfile(source):
        shutil.copy(source, destination)
        print(f"Copied {file} to {destination}")

print("Done!")
