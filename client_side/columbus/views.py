from django.http import HttpResponse
from django.shortcuts import render
import json
import asyncio
import aiohttp
import platform
from random import randint
import time

if platform.system() == 'Windows':
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
    print(res)
    if 'signal' in res:
        return "Runtime Error"
    status = res['status']
    if status == '0':
        return res['program_output'].strip()
    elif status == '1':
        if len(res['compiler_error']) != 0:
            return "Compile Time Error\n\n"+res['compiler_error'].strip()
        return "Compile Time Error\n\n"+res['program_error'].strip()
    elif status == '69':
        return "Time Limit Exceeded"
    else:
        return "Unexpected Error occurred"


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


async def compileCode(session, timeout, code="",ext='py'):
    sample = option_templates[ext]
    sample['code'] = code
    res = await makeCompileRequest(session, sample, timeout)
    return res


def get_tasks(session, code, ext='py'):
    tasks = [asyncio.create_task(compileCode(session, default_timeout, code, ext))]
    return tasks


async def runTask(code, ext='py'):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session, code, ext)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(parseResponse(response))
    return results


async def api_latency(timeout):
    async with aiohttp.ClientSession() as session:
        start = time.time()
        await compileCode(session, 'data/sample.cpp', timeout)
        end = time.time()
        latency = end-start
        return latency


def homePage(request):
    try:
        if request.method == 'POST':
            text = request.POST.get('text')
            language = request.POST.get('language')
            # FILE UPLOAD DOESNT WORK, I've commented out the code in index.html
            # file = request.FILES['source_file']

            if text:
                code = text
                results = asyncio.run(runTask(code, language))
                return render(request,"index2.html", {"resp":results[0]})
    except:
        pass
    return render(request,"index.html")