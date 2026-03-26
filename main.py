import json
with open('/tmp/push_data.json', 'r') as f:
    data = json.load(f)
print(data[0]['content'])