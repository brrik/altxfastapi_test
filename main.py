import os
import gspread
import datetime
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware # CORS
from oauth2client.service_account import ServiceAccountCredentials

# CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Auth = "./norse-lotus-423606-i2-353a26d9cd49.json"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Auth
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(Auth, scope)
Client = gspread.authorize(credentials)

SpreadSheet = Client.open_by_key("1eTYSRjB5TpIXwJQVCFCn8V32wZ_kPK1etwqgvaEa5Oo")
mainSheet = SpreadSheet.worksheet("Main")
userDataSheet = SpreadSheet.worksheet("UserData")

@app.post("/postdata/")
async def addRow(request: Request):
    try:
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y年%m月%d日 %H:%M:%S')
        json_data = await request.json()
        roll = json_data.get("roll")
        data  = json_data.get("data")
        mainSheet.append_row([now, roll, data])
        return True
    except:
        return False

@app.get("/getalldata")
async def getData():
    try:
        return_data = mainSheet.get_all_values()
        return return_data
    except:
        return False
    
@app.get("/getrolldata/{roll}")
async def getRollData(roll):
    try:
        roll_dict = {
            "sh":["社長","事業部長","部長","課長","GL","その他"],
            "jb":["事業部長","部長","課長","GL","その他"],
            "bc":["部長","課長","GL","その他"],
            "kc":["課長","GL","その他"],
            "gl":["GL","その他"],
            "ot":"その他"
            }
        main_data = mainSheet.get_all_values()
        print(roll_dict[roll])
        roll_based_list = filter_by_roll(main_data,roll_dict[roll])
        return roll_based_list
    except:
        return False

@app.get("/login/{user_name}/{password}")
def checkLogin(user_name,password):
    try:
        user_datas = userDataSheet.get_all_values()
        for data in user_datas:
            if data[0] == user_name and data[1] == password:
                return data[2]
        else:
            return False
    except:
        return False

@app.post("/login/adduser/")
def addUserData(request: Request):
    try:
        json_data = request.json()
        user_id = json_data.get("userid")
        user_pass = json_data.get("pass")
        user_roll = json_data.get("roll")
        userDataSheet.append_row([user_id,user_pass,user_roll])
    except:
        return False

def filter_by_roll(data,roll):
    return_list = []
    for i in data:
        if i[1] in roll:
            return_list.append(i)
    
    return return_list