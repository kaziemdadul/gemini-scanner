import re

with open("panels.txt", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

new_panels = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    if "|" in line:
        url, key = line.split("|", 1)
        url = url.strip()
        key = key.strip()
        if not key:
            key = url
    else:
        url = line.strip()
        key = url
    
    new_panels.append((url, key))

with open("gemini18msc.py", "r", encoding="utf-8") as f:
    content = f.read()

# find the existing panels to avoid duplicates
existing_urls = set(re.findall(r'"(https://[^"]+)"', content))

panels_to_add = []
for url, key in new_panels:
    if url not in existing_urls:
        panels_to_add.append(f'    ("{url}", "{key}"),')

if panels_to_add:
    addition = "\n    # ===== PANELS FROM panels.txt =====\n" + "\n".join(panels_to_add) + "\n"
    
    # Insert before the closing bracket of FIREBASE_PANELS
    # The list ends with:
    #     ("https://sastaapp-394cd-default-rtdb.firebaseio.com", "https://sastaapp-394cd-default-rtdb.firebaseio.com"),
    # ]
    
    # find ] that closes FIREBASE_PANELS
    pattern = r'(\n\])'
    match = re.search(pattern, content)
    if match:
        parts = re.split(r'\n\]', content, maxsplit=1)
        new_content = parts[0] + addition + "\n]" + parts[1]
        
        with open("gemini18msc.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Added {len(panels_to_add)} panels.")
    else:
        print("Could not find the end of FIREBASE_PANELS.")
else:
    print("No new panels to add.")
