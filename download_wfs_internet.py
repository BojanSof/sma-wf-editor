import os
import requests

# retrieved from app data folder
base_url = r"https://api-oss.iot-solution.net/watchFace/JL/AM08/default/category"
categories = [
    "dynamic1",
    "exercise2",
    "business3",
    "machinery4",
    "simple5",
    "illustration6",
]

base_save_dir = os.path.join("watch_faces", "internet")
os.makedirs(base_save_dir, exist_ok=True)

max_num = 80

for k, category in enumerate(categories):
    working_on_category = True
    for i in range(1, max_num):
        if not working_on_category:
            print(f"Finished downloading category {category}")
            break
        file_name = f"{k+1}00{i:02d}.bin"
        url = f"{base_url}/{category}/{file_name}"
        r = requests.get(url)
        if r.status_code != 200:
            working_on_category = False
        else:
            print(f"Saving file {file_name}...")
            with open(os.path.join(base_save_dir, file_name), "wb") as f:
                f.write(r.content)
