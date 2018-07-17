#! /usr/local/bin/python3
import sys; print('Python %s on %s' % (sys.version, sys.platform))
import vk
import time
import datetime
import sqlite3
import threading
# Initial settings
id1 = 442615506
id2 = 74166444
SLEEP_TIME = 1
LOCATE_DB = '/data/user.sqlite3'
LOCK = threading.RLock()
session = vk.Session(access_token='6f80043ae9ac52f0ca1a59538ba0fbaad523639406ec97773daa044be8f9d32ff8990da18b549c894d5cd')
vkapi = vk.API(session, v=5.80)

#General func
def get_status_online(usrID):
    LOCK.acquire()
    try:
        time.sleep(SLEEP_TIME)
        tmpInfo = vkapi.users.get(user_id=usrID, fields='online')
        LOCK.release()
        return tmpInfo[0]['online']
    except:
        LOCK.release()
        print("Error: get_status_online")
        return(0)


def get_last_online(usrID):
    LOCK.acquire()
    try:
        time.sleep(SLEEP_TIME)
        tmpInfo = vkapi.users.get(user_id=usrID, fields='last_seen')
        LOCK.release()
        return (
            datetime.datetime.fromtimestamp(
                int(tmpInfo[0]['last_seen']['time']))
        ).strftime('%Y-%m-%d_%H:%M:%S')
    except:
        LOCK.release()
        print("Error: get_last_online")
        return("ERROR")


def get_last_platform(usrID):
    LOCK.acquire()
    try:
        time.sleep(SLEEP_TIME)
        tmpInfo = vkapi.users.get(user_id=usrID, fields='last_seen')
        LOCK.release()
        if tmpInfo[0]['last_seen']['platform'] == 1:
            return ("Mobile")
        if tmpInfo[0]['last_seen']['platform'] == 2:
            return ("iPhone")
        if tmpInfo[0]['last_seen']['platform'] == 3:
            return ("iPad")
        if tmpInfo[0]['last_seen']['platform'] == 4:
            return ("Android")
        if tmpInfo[0]['last_seen']['platform'] == 5:
            return ("WP")
        if tmpInfo[0]['last_seen']['platform'] == 6:
            return ("W10")
        if tmpInfo[0]['last_seen']['platform'] == 7:
            return ("PC")
        if tmpInfo[0]['last_seen']['platform'] == 8:
            return ("VK_Mobile")
        else:
            return (tmpInfo[0]['last_seen']['platform'])
    except:
        LOCK.release()
        print("Error: enter_online_data")
        return("ERROR")



def enter_online_data(tmptime, tmponline, tmpplatform, tmpuser):
    LOCK.acquire()
    try:
        now = datetime.datetime.now()
        sql = sqlite3.connect(LOCATE_DB)
        dbTarget = sql.cursor()
        dbTarget.execute("insert into act (time, online, platform, user, current_time) values (?, ?, ?, ?, ?)",
                         (tmptime, tmponline, tmpplatform, tmpuser, now.strftime('%Y-%m-%d_%H:%M:%S')))
        sql.commit()
        sql.close()
        LOCK.release()
    except:
        LOCK.release()
        print("Error: enter_online_data")

def status_detect(usrCheck):
    LOCK.acquire()
    # SQL connect
    sql = sqlite3.connect(LOCATE_DB)
    dbTarget = sql.cursor()
    # VK check
    tmp_last_online = get_last_online(usrCheck)
    tmp_status = get_status_online(usrCheck)
    tmp_platform = get_last_platform(usrCheck)
    if (tmp_last_online == "ERROR" or tmp_status == "ERROR" or tmp_platform == "ERROR"):
        sql.close()
        LOCK.release()
        print("Error: status_detect")
    else:
        enter_online_data(tmp_last_online, tmp_status, tmp_platform, usrCheck)
        if tmp_status == 1:
            print("Detect online:", tmp_last_online, " platform:", tmp_platform, " user:", usrCheck, "worktime:",
                  str(datetime.datetime.now()))
        if tmp_status == 0:
            print("Detect offline:", tmp_last_online, " platform:", tmp_platform, " user:", usrCheck, "worktime:",
                  str(datetime.datetime.now()))
        sql.close()
        LOCK.release()

def UserCheck(ID, index):
    iterat = 0
    while True:
        iterat = 0
        while ((get_status_online(ID) == 1) and (iterat == 0)):
            status_detect(ID)
            while ((iterat < 30) and (get_status_online(ID) == 1)):
                time.sleep(1)
                iterat = iterat + 1

        iterat = 0
        while ((get_status_online(ID) == 0) and (iterat == 0)):
            status_detect(ID)
            while ((iterat < 180) and (get_status_online(ID) == 0)):
                time.sleep(1)
                iterat = iterat + 1

def ThreadInit(tmpIDs):
    i = 0
    ts = list()
    for i in range(len(tmpIDs)):
        ts.append(threading.Thread(target=UserCheck, args=(tmpIDs[i], i)))
    for i in range(len(tmpIDs)):
        ts[i].daemon = True
    for i in range(len(tmpIDs)):
        ts[i].start()
    for i in range(len(tmpIDs)):
        ts[i].join()

#Main
IDs = list()
IDs.append(442615506)
IDs.append(74166444)

print(IDs[0])
print(IDs[1])

ThreadInit(IDs)

input()
