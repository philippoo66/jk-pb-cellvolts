'''
   Copyright 2025 philippoo66
   
   Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.gnu.org/licenses/gpl-3.0.html

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import time
import threading
import paho.mqtt.client as paho


# MQTT-Broker Infos
broker = "192.168.1.106"  # adjust IP here!


verbose = False
exit_flag = False

mqtt_client = None
publ_queue = []


# def on_connect(client, userdata, flags, reason_code, properties):
#     listen_list = []
#     if(settings_ini.mqtt_listen_cmnd != None):
#         #client.subscribe(settings_ini.mqtt_listen)
#         listen_list = [(settings_ini.mqtt_listen_cmnd,0)]
#     listen_list += settings_ini.mqtt_listen_mpp
#     listen_list += settings_ini.mqtt_listen_battsys
#     listen_list += settings_ini.mqtt_listen_wwheat
#     if(len(listen_list) > 0):
#         client.subscribe(listen_list)
#         #print("H listen_list", listen_list)
#     #ret = mqtt_client.publish(settings_ini.mqtt_topic + "/LWT" , "online", qos=0,  retain=True)

    
def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print('mqtt broker disconnected. reason_code = ' + str(reason_code))
    #ret = mqtt_client.publish(settings_ini.mqtt_topic + "/LWT" , "offline", qos=0,  retain=True)

# def on_message(client, userdata, msg):
#     #print("MQTT recd:", msg.topic, msg.payload)
#     if(settings_ini.mqtt_listen_cmnd is None):
#         print("MQTT_err:", msg.topic, msg.payload)  # ErrMsg oder so?
#         return
    
#     try:
#         topic = str(msg.topic)            # Topic in String umwandeln
#         #print(topic)

#         for i in range(num_mppmodes):
#             top, qos = settings_ini.mqtt_listen_mpp[i]
#             if(topic == top):
#                 payload = json.loads(msg.payload.decode())  # Payload in Dict umwandeln
#                 mppmodes[i] = int(payload["value"])
#                 powercontrol.recent_venus_receive = time.time()
#                 #print(topic, mppmodes[i])
#                 #print(mppmodes)
#                 return
        
#         for i in range(num_batt_infos):
#             top, qos = settings_ini.mqtt_listen_battsys[i]
#             if(topic == top):
#                 payload = json.loads(msg.payload.decode())  # Payload in Dict umwandeln
#                 battsysinfos[i] = float(payload["value"])
#                 powercontrol.recent_venus_receive = time.time()
#                 # if(i == 5):
#                 #     print(time.time(), topic, battsysinfos[i])
#                 #print(battsysinfos)
#                 return

#         for i in range(num_wwheat_infos):
#             top, qos = settings_ini.mqtt_listen_wwheat[i]
#             if(topic == top):
#                 rec = clean_string(msg.payload)
#                 wwheatinfos[i] = float(rec)
#                 #print(wwheatinfos)
#                 return

#         if(settings_ini.mqtt_listen_cmnd is not None):
#             if topic == settings_ini.mqtt_listen_cmnd:
#                 rec = clean_string(msg.payload)
#                 #cmnd_queue.append(rec) 
#                 perform_command(rec)
#                 return

#         print("MQTT_extra:", msg.topic, msg.payload)
#     except Exception as e:
#         print("Err_on_message:", e)


# def on_subscribe(client, userdata, mid, reason_code_list, properties):
#     # Since we subscribed only for a single channel, reason_code_list contains
#     # a single entry
#     if reason_code_list[0].is_failure:
#         print(f"Broker rejected you subscription: {reason_code_list[0]}")
#     else:
#         print(f"Broker granted the following QoS: {reason_code_list[0].value}")


def connect_mqtt():
    global mqtt_client
    try:
        # Verbindung zu MQTT Broker herstellen ++++++++++++++
        mqtt_client = paho.Client(paho.CallbackAPIVersion.VERSION2, "jkpbcv") # + '_' + str(int(time.time()*1000)))  # Unique mqtt id using timestamp
        # if(settings_ini.mqtt_user != None):
        #     mlst = settings_ini.mqtt_user.split(':')
        #     mqtt_client.username_pw_set(mlst[0], password=mlst[1])
        # mqtt_client.on_connect = on_connect
        mqtt_client.on_disconnect = on_disconnect
        # mqtt_client.on_message = on_message
        #mqtt_client.will_set(settings_ini.mqtt_topic + "/LWT", "offline", qos=0,  retain=True)
        # if(settings_ini.mqtt_listen_cmnd != None):
        #     mqtt_client.on_subscribe = on_subscribe
        # mlst = settings_ini.mqtt.split(':')
        mqtt_client.connect("192.168.1.106")
        mqtt_client.reconnect_delay_set(min_delay=1, max_delay=30)
        mqtt_client.loop_start()

        # MQTT publishing might take some longer so we use a queue
        publish_thread = threading.Thread(target=publish_loop)
        publish_thread.daemon = True  # Setze den Thread als Hintergrundthread - wichtig fuer Ctrl-C
        publish_thread.start()
    except Exception as e:
        raise Exception("Error connecting MQTT: " + str(e))


def add2queue(name, value):
    # try:
    #     value = float(value)
    # except:
    #     pass
    if(value is not None):
        tup = ("Jkpbcv/" + name, value)
        publ_queue.append(tup)

def addraw2queue(topic, value, prio=False):
    tup = (topic, value)
    if(prio):
        publ_queue.insert(0, tup)
    else:    
        publ_queue.append(tup)

def publish_loop():
    while(not exit_flag):
        if(len(publ_queue) > 0):
            tup = publ_queue.pop(0)
            if(mqtt_client != None):
                ret = mqtt_client.publish(tup[0], tup[1])    
                if(verbose): print(ret)
        time.sleep(0.02)


def exit_mqtt():
    global exit_flag
    exit_flag = True
    if(mqtt_client != None):
        print("disconnect MQTT client")
        mqtt_client.disconnect()

# # utils ----------
# def clean_string(payload) -> str:
#     rec = utils.bstr2str(payload)
#     rec = rec.replace(' ','').replace('\0','').replace('\n','').replace('\r','').replace('"','').replace("'","")
#     return rec

    
# ------------------------
# main for test only
# ------------------------
def main():
    try:
        connect_mqtt()
        print("connect ok")
        while(True):
            for i in range(10):
                #publish_read("TestVal", 0x0123, i)
                mqtt_client.publish(f"Mqtttest/TestVal", i)
                time.sleep(3)
        # else:
        #     print("fail")
    except Exception as e:
        print(e)
    finally:
        exit_mqtt()


if __name__ == "__main__":
    main()
