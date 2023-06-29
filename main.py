import json
import uuid
from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any

from job.ManageData import ManageData

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))


@app.get("/")
async def main():
    return FileResponse("public/index.html")


@app.get("/regions")
async def regions():
    result = ManageData.get_regions()
    return json.dumps(result)


@app.get("/vacancies")
async def vacancies(word: str = '', status: str = '', region: str = ''):
    result = ManageData.get_vacancies(keyword=word, status=status, region=region)
    return json.dumps(result)


@app.post("/action")
async def action(payload: Dict[Any, Any]):
    print(f'Payload: {payload}')
    action_type, vacancy_id = payload['action'].split('_')
    ManageData.add_action(action_type, vacancy_id, payload['text'])

    #  Ещё вариант параметров:
    # https://metanit.com/python/fastapi/1.10.php
    # action_type, vacancy_id = action.split('_')
    # result = ManageData.add_action(action_type, vacancy_id, text)
    pass
