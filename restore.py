import zipfile
import os

zip_path = r"C:\Users\inbav\Downloads\sih26074-main (4).zip"
target_dir = r"C:\Users\inbav\Downloads\sih26074-main\sih26074-main"

files_to_restore = [
    "sih26074-main/src/dashboard/static/css/style.css",
    "sih26074-main/src/dashboard/static/js/tabs/dashboard.js",
    "sih26074-main/src/dashboard/static/js/tabs/map.js",
    "sih26074-main/src/dashboard/static/js/tabs/downscaling.js",
    "sih26074-main/src/dashboard/static/js/tabs/advisory.js",
    "sih26074-main/src/dashboard/static/js/tabs/validation.js",
    "sih26074-main/src/dashboard/static/js/tabs/risk.js",
    "sih26074-main/src/dashboard/static/js/tabs/feedback.js"
]

with zipfile.ZipFile(zip_path, 'r') as z:
    for f in files_to_restore:
        # Extract the content and save it to the correct path
        try:
            content = z.read(f)
            out_path = os.path.join(target_dir, f.replace("sih26074-main/", ""))
            with open(out_path, "wb") as out_f:
                out_f.write(content)
            print(f"Restored {f}")
        except KeyError:
            print(f"Not found in zip: {f}")
