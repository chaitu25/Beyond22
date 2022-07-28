import aiohttp
import websockets
from pydantic import BaseModel
from fastapi import FastAPI, Request, Response, WebSocketDisconnect
from starlette.websockets import WebSocket, WebSocketState
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
import pandas as pd
import uuid
import sqlite3
app = FastAPI()

RASAURL = "http://localhost:5005/webhooks/rest/webhook/"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RasaResponse:
    def __init__(self, response):
        # input :
        # a list of { "recipient_id": id, "text": msg} dicts
        try:
            self.response_json = []
            id = response[0]['recipient_id']
            utterances = [x['text'] for x in response]
            for ut in utterances:
                self.response_json.append({"recipient_id": id, "text": ut})
        except:
            print("Bad rasa response")
            # traceback.print_exc()
            self.response_json = []
            return

    def get_response_list(self):
        if self.response_json:
            return [x["text"] for x in self.response_json]
        else:
            return ""

    def get_response_string(self):
        if self.response_json:
            responses_list = [x["text"] for x in self.response_json]
            return "\n".join(responses_list)
        else:
            return ""

    def get_recipient_id(self):
        if self.response_json:
            return self.response_json[0]['recipient_id']
        else:
            return ""


class FeedbackRequest(BaseModel):
    user_id: str
    rating1: str
    rating2: str


class RasaClientMessage(BaseModel):
    message: str
    sender: str


class WizardInfo():
    def __init__(self, wid, websocket):
        self.wizard_id = wid
        self.websocket = websocket
        self.current_client = -1
        self.incoming_queue = asyncio.Queue()

    def get_client(self):
        return self.current_client

    def assign_client(self, cid):
        self.current_client = cid

    def unassign_client(self):
        self.current_client = -1


class ConnectionManager:
    def __init__(self):
        self.active_wizards = None
        self.clients = set()
        self.next_wid = 0
        self.wizard_onetime_tickets = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        new_wizard_info = WizardInfo(self.next_wid, websocket)
        self.active_wizards = new_wizard_info
        self.next_wid += 1
        print(str(new_wizard_info))
        return new_wizard_info

    def disconnect(self, websocket: WebSocket):
        for wid, wizard_info in self.active_wizards.items():
            if wizard_info.websocket == websocket:
                # also delete the wizard_info.incoming_queue here
                self.active_wizards.pop(wid)
                print("Wizard with id {} has disconnected".format(
                    wizard_info.wizard_id))
                orphan_client_id = wizard_info.get_client()
                if orphan_client_id == -1:
                    return
                print("Client {} is now on his own".format(orphan_client_id))
                self.unassigned_clients.append(orphan_client_id)
                self.assigned_clients.pop(orphan_client_id)
                return

    def addClient(self, client_id):
        if client_id not in self.clients:
            self.clients.add(client_id)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def renew_keep_alive(self, client_id):
        print("Renewing keepaline for client {}...".format(client_id))
        if client_id in self.assigned_clients:
            self.assigned_clients[client_id].last_connection_time = dt.now()
        else:
            print("No need to renew time for a client that is not assigend to wizard.")

        return


manager = ConnectionManager()


async def tell_rasa(rasaurl, sender, message):

    try:
        async with aiohttp.request('POST', rasaurl, json={'sender': sender, 'message': message}) as resp:
            assert resp.status == 200
            result = await resp.json(encoding='utf-8')

            return result
    except aiohttp.ServerConnectionError as e:
        print("Connection Error")
        raise aiohttp.ServerConnectionError


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/webhooks/rest/webhook/')
async def post(msg: RasaClientMessage):
    manager.addClient(msg.sender)
    response_dict = await tell_rasa(RASAURL, msg.sender, msg.message)
    if manager.active_wizards:
        try:
            wizard_queue = manager.active_wizards.incoming_queue
            wizard_websocket = manager.active_wizards.websocket
            res = {}
            res['message'] = msg.message
            res['response'] = response_dict[0]['text']
            await wizard_websocket.send_text(json.dumps(res))
            wizard_res_dict = await wizard_queue.get()
            data = {'Message': msg.message, 'Response':
                    response_dict[0]['text'], 'Expert_Response': wizard_res_dict}
            # df = pd.DataFrame(traingData)
            # df.to_csv('trainingData.csv', header=False, index=False, mode='a')
            # print('New Data Recorded')
            # print(wizard_res_dict)
            response_dict[0]['text'] = wizard_res_dict
            con = sqlite3.connect('edgepattern.db')
            cur = con.cursor()
            cur.execute('''Select count(name) FROM sqlite_master WHERE type='table'
  AND name='trainingData';''')
            if cur.fetchone()[0] != 1:
                cur = con.execute(
                    'CREATE TABLE trainingData(Message VARCHAR2(100), Response VARCHAR2(100),Expert_Response VARCHAR2(100))')
            cur.execute(
                'INSERT INTO trainingData(Message,Response,Expert_Response) VALUES (?,?,?);', (res['message'], res['response'], str(wizard_res_dict)))
            con.commit()
            print('New Data Recorded')
            # print("For client {} we got {}".format(msg.sender, wizard_json))
        except Exception as e:
            print('error = ', e)
        finally:
            cur.close()
            con.close()
    return response_dict


@ app.post('/feedback')
async def post(msg: FeedbackRequest):
    print(msg.user_id)
    res = {'user_id': [msg.user_id],
           'feedback1': [msg.rating1], 'feedback2': [msg.rating2]}
    df = pd.DataFrame(res)
    df.to_csv('feedback.csv', header=False, index=False, mode='a')
    print('Feedback Recorded')
    return res


@ app.websocket("/wizard_ws")
async def speech_to_text(websocket: WebSocket):
    print('Wizard connected!')
    wizard_info = await manager.connect(websocket)
    try:
        # await websocket.send_text("Hello")
        while True:
            new_message = await websocket.receive_text()
            print(new_message)
        # Shutdown is an example; as of now no such message is sent by the clients
            # if new_message != "SHUTDOWN":
            # TODO: ensure message has the correct form
            # expecting json of form
            # {'client_id': client_id,
            #  'response': response} a string containing an integer
            await wizard_info.incoming_queue.put(new_message)
    except WebSocketDisconnect:
        print("Connection closed")
    # traceback.print_exc()
        manager.disconnect(websocket)
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed")
    # traceback.print_exc()
        manager.disconnect(websocket)
        return


def extract_user_id(response_dict):
    # more than one messages consists of the prompted message to the user
    return response_dict[0]["recipient_id"]
