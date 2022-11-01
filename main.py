import asyncio
import aiohttp
import platform
import json
from random import randint
import time

if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
with open('option_templates.json', 'r') as f:
    option_templates = json.load(f)

api_url = 'https://wandbox.org/api'
default_timeout = 5
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def readCode(path):
    with open(path, 'r') as f:
        code = f.readlines()
    return "".join(code)


def parseResponse(res):
    if 'signal' in res:
        return "RTE"
    status = res['status']
    if status == '0':
        return res['program_output'].strip()
    elif status == '1':
        if len(res['compiler_error']) != '0':
            return "CTE"
        return res['program_error'].strip()
    elif status == '69':
        return "TLE"
    else:
        return "Unexpected Error"


def makeTimeout(n):
    return aiohttp.ClientTimeout(total=n)


async def makeCompileRequest(session, data, timeout=default_timeout, retry=0):

    payload = json.dumps(data)
    url = api_url + '/compile.json'
    try:
        response = await session.post(url, data=payload, headers=headers, timeout=makeTimeout(timeout),ssl=False)
        response.raise_for_status()
    except asyncio.exceptions.TimeoutError as e:
        if retry == 0:
            return await makeCompileRequest(session, data, timeout, 1)
        return {'status':'69', 'message':'TLE'}
    try:
        # return response.json(cls=ndjson.Decoder)
        return await response.json()
    except json.decoder.JSONDecodeError as e:
        return {"status": 500, "message": "JSON Error"}


async def compileCode(session, file, timeout):
    ext = file.split('.')[-1]
    sample = option_templates[ext]
    sample['code'] = readCode(file)
    res = await makeCompileRequest(session, sample, timeout)
    return res

results = []


def get_tasks(session, task_list):
    tasks = []
    for data in task_list:
        tasks.append(asyncio.create_task(compileCode(session, data, default_timeout)))
    return tasks


async def runTask(task_list):
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session, task_list)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(parseResponse(response))


async def api_latency(timeout):
    async with aiohttp.ClientSession() as session:
        start = time.time()
        await compileCode(session, 'data/sample.cpp', timeout)
        end = time.time()
        latency = end-start
        return latency


def main():
    api_lat = asyncio.run(api_latency(default_timeout))
    print(api_lat)
    start = time.time()
    temp = ['data/sample.py', 'data/sample.cpp']
    taskList = []
    for i in range(5):
        taskList.append(temp[randint(0, 1)])
    asyncio.run(runTask(taskList))
    end = time.time()
    total_time = end - start
    print("Time: ", max(0,total_time - api_lat))
    for ele in results:
        print(ele)


if __name__ == "__main__":
    main()