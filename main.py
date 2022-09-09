# from unittest import async_case
from datetime import datetime
import json
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prisma import Prisma
from bcrypt import *
import requests
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
db = Prisma()


templates = Jinja2Templates(directory="template")


@app.get("/", response_class=HTMLResponse)
async def root(req: Request):
    return templates.TemplateResponse('login.html', {"request": req, })


@app.get('/Registeration', response_class=HTMLResponse)
async def Registeration(req: Request):
    return templates.TemplateResponse('Registeration.html', {'request': req})


@app.post('/login')
async def login(req: Request, res: Response, email: str = Form(), password: str = Form(),):
    user = await db.user.find_unique({
        'email': email
    })
    if user:
        if checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            _res = Response("DONE")
            _res.set_cookie("id", user.id)
            return _res
        else:
            return Response({
                'states': 500,
                'message': 'data incrreated'
            }, 500)

    else:
        return Response({
            'states': 500,
            'message': 'data incrreated'
        }, 500)


@app.post('/Registeration/add')
async def Registeration(res: Response, email: str = Form(), password: str = Form(), username: str = Form()):
    password = hashpw(password.encode('utf-8'), gensalt(14))
    data = await db.user.create({
        'email': email,
        'password': bytes(password).decode('utf-8'),
        'username': username,
    })
    _res = Response("DONE")
    _res.set_cookie("id", data.id)
    return _res


@app.get('/home', response_class=HTMLResponse)
async def home(req: Request):
    joke = requests.get('https://icanhazdadjoke.com/', headers={
        'Accept': 'application/json'
    }).json()
    print(joke)
    user = await db.user.find_unique({'id': req.cookies['id']}, include={
        'Task': True
    })
    d = []
    c = []
    a = []
    for i in user.Task:
        if i.isDelete:
            d.append(i)
        elif i.isComplete:
            c.append(i)
        else:
            a.append(i)
    # print(user)

    return templates.TemplateResponse('home.html', {'request': req, 'data': user, '_activ': a, 'delete': json.dumps(d, indent=4, sort_keys=True, default=str), '_delete': d, 'complete': json.dumps(c, indent=4, sort_keys=True, default=str), '_complete': c, 'joke': joke['joke'], "a": json.dumps(user.dict(), indent=4, sort_keys=True, default=str)})


@app.post('/add/tesk')
async def addt(req: Request, cata_name: str = Form(), what: str = Form(), when: str = Form()):
    T = await db.task.create({
        'isComplete': False,
        'isDelete': False,
        'user': {
            'connect': {
                'id': req.cookies['id']
            }
        },
        'what': what,
        'When': datetime.fromisoformat(when),
        'cata': {
            'create': {
                'name': cata_name
            }
        }
    })
    return T


@app.post('/complite/tesk/{id}')
async def addt(req: Request, id: str):
    T = await db.task.update({
        'isComplete': True
    }, {
        'id': id
    })
    return T


@app.post('/delete/tesk/{id}')
async def addt(req: Request, id: str):
    T = await db.task.update({
        'isDelete': True
    }, {
        'id': id
    })
    return T


@app.get('/user')
async def userPage(req: Request):
    user = await db.user.find_unique({'id': req.cookies['id']})
    joke = requests.get('https://icanhazdadjoke.com/', headers={
        'Accept': 'application/json'
    }).json()
    return templates.TemplateResponse('user.html', {'request': req, 'user': user, 'joke': joke['joke']})


@app.on_event('startup')
async def main():
    await db.connect()
