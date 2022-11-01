# # code input from files, one function to take code and upload it and get response
import json
# import ndjson
from requests import post
# import aiohttp
# import asyncio
with open('option_templates.json', 'r') as f:
    option_templates = json.load(f)
import time
def readCode(path):
    with open(path, 'r') as f:
        code = f.readlines()
    return "".join(code)
x = time.time()
api_url = 'https://wandbox.org/api'
default_timeout = 5
payload = option_templates['py']
payload['code'] = readCode('data/sample.cpp')
payload = json.dumps(payload)
print(payload)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
url = api_url + '/compile.json'
response = post(url, data=payload, headers=headers, timeout=5)
print(time.time()-x)
print(response.json())

#
#
# def makeCompileRequest(data, timeout=default_timeout):
#     headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
#     payload = json.dumps(data)
#     url = api_url + '/compile.json'
#     # url = api_url + '/compile.ndjson'
#     try:
#         response = requests.post(url, data=payload, headers=headers, stream=True, timeout=timeout)
#         response.raise_for_status()
#     except requests.exceptions.ReadTimeout as e:
#         return {'status': '69'}
#     try:
#         # return response.json(cls=ndjson.Decoder)
#         return response.json()
#     except json.decoder.JSONDecodeError as e:
#         return {"status": 500, "message": "JSON Error"}
#
#
# def readCode(path):
#     with open(path, 'r') as f:
#         code = f.readlines()
#     return "".join(code)
#
#
# def parseResponse(res):
#     if 'signal' in res:
#         return "RTE"
#     status = res['status']
#     if status == '0':
#         return res['program_output'].strip()
#     elif status == '1':
#         return res['program_error'].strip()
#     elif status == '69':
#         return "TLE"
#     else:
#         return "Unexpected Error"
#
#
# def compileCode(file, timeout):
#     ext = file.split('.')[-1]
#     sample = option_templates[ext]
#     sample['code'] = readCode(file)
#     res = makeCompileRequest(sample, timeout)
#     print(parseResponse(res))
#
#
# def get_tasks(url, headers, task_list, session):
#     tasks = []
#     for data in task_list:
#         tasks.append(asyncio.create_task(session.post(url, data=data, headers=headers)))
#     return tasks
#
#
# results = []
#
#
# async def submitBatch():
#     async with aiohttp.ClientSession() as session:
#         tasks = get_tasks(api_url, session)
#
#         responses = await asyncio.gather(*tasks)
#         for response in responses:
#             results.append(await response.json())
#
#
# def main():
#     # compileCode('data/sample.cpp', default_timeout)
#     # compileCode('data/sample.cpp', default_timeout)
#     # compileCode('data/sample.py', default_timeout)
#     # compileCode('data/sample.cpp', default_timeout)
#     # compileCode('data/sample.py', default_timeout)
#     asyncio.run(submitBatch())
#
#
# if __name__ == "__main__":
#     main()
