# coding: utf-8
import serial 
# In[4]:


# read keys 
import json 
import time 
import base64 
import requests 
import cv2


with open("./keys", "r") as f: 
    keys = json.load(f) 


# In[5]:


keys['content-type'] = 'application/json'


# In[6]:

import random 
cv2.namedWindow("preview") 
vc = cv2.VideoCapture(0)


# In[17]:


# from multiprocessing import Queue, Event, Process 

# request_event = Event() 
# complete_event = Event() 
# term_event = Event() 

# frame_queue = Queue() 
# res_queue = Queue() 
# class Detector(Process): 
#     def __init__(self, frame_queue, res_queue, request_event, term_event, complete_event, headers): 
#         super(Detector, self).__init__() 
#         self.frame_comm = frame_queue
#         self.res_comm = res_queue
#         self.request_event = request_event 
#         self.term_event = term_event
#         self.complete_event = complete_event
#         self.headers = headers 

#     def run(self): 
#         url = "https://api.kairos.com/detect"
#         while not self.term_event.is_set():
#             # block until we get a request 
#             self.request_event.wait() 
#             # now it's set 
#             # read from frame 
#             small_frame = self.frame_comm.get() 

            # _, png = cv2.imencode(".jpg", small_frame)
            # saved_data = base64.b64encode(png).decode('ascii') 
            # payload = json.dumps({"image": saved_data}) 
#             try: 
#                 print("sending...")
#                 response = requests.post(url, headers = self.headers, data=payload, timeout = 1)
#                 print("received")
#             except: 
#                 print("issue raised")
#                 raise 
#             self.res_comm.put(response)
#             self.request_event.clear() 
#             self.complete_event.set() 
            


# In[18]:


start_time = time.time() 
end_time = time.time() 
if vc.isOpened(): 
    rval, frame = vc.read() 
    
else: 
    rval = False 


saved = ""
frame = frame[:, 280:-280, :]
# doer = Detector(frame_queue, res_queue, request_event=request_event, term_event=term_event, complete_event=complete_event, headers=keys)
# doer.start() 
url = "https://api.kairos.com/detect"


from requests_futures.sessions import FuturesSession 



def response_hook(resp, *args, **kwargs): 
    resp.data = resp.json() 

waiting = False 

count = 0 

ser_port = serial.Serial('/dev/cu.usbmodem14201')
additional_text = ""
def slap(): 
    ser_port.write(b'A')
    time.sleep(0.5)
    ser_port.write(b'B')

slap_enable = False 
slap_on = True
while rval: 
    end_time = time.time() 
    fps = 1/(end_time - start_time)
    start_time = time.time() 
    
    cv2.imshow("preview", frame) 
    rval, frame = vc.read() 
    frame = cv2.flip(frame, 1)[:, 280:-280, :]

    if not waiting: 
        session = FuturesSession(max_workers=10) 
        session.headers.update(keys)

        small_frame = cv2.resize(frame, (256,256), 0, 0, cv2.INTER_CUBIC) 
        _, png = cv2.imencode(".jpg", small_frame)
        saved_data = base64.b64encode(png).decode('ascii') 
        payload = json.dumps({"image": saved_data}) 
        future = session.post(url, data=payload, timeout=5, hooks = {
            "response": response_hook
        })
        waiting = True 

    if waiting: 
        if future.done(): 
            try: 
                response = future.result() 
            except: 
                session.close() 
                waiting = False
                print("Stopped again")
                continue
                # clean up and re-try 
            waiting = False 
            try: 
                res = response.data['images'][0]['faces'][0]['attributes']
                res.pop('age') 
                res.pop('glasses')
                res.pop('gender')
                res.pop('lips')
                order = list(sorted(res.items(), key=lambda x: x[1], reverse=True))
                if order[0][0] == 'white': 
                    if random.random() < .9: 
                        slap_enable = True
                elif order[0][0] == 'asian': 
                    if random.random() < .25: 
                        slap_enable = True
                else: 
                    if random.random() < .18: 
                        slap_enable = True 
            except: 
                pass 
    
    # cv2.putText(frame, additional_text, (360, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2, cv2.LINE_AA)

    cv2.putText(frame, 'Frame Rate: {:.2f}'.format(fps), (10,20),
        cv2.FONT_HERSHEY_PLAIN, 1, 255, 2, cv2.LINE_AA, False)
    if slap_enable and slap_on: 
        slap() 
        slap_enable = False 
    if not slap_on: 
        cv2.putText(frame, 'Slaps Disabled', (10, 40), cv2.FONT_HERSHEY_PLAIN, 1, 255, 2, cv2.LINE_AA)
    key = cv2.waitKey(20) 
    if key == 27: 
        break 

    if key == 32: 
        slap_on = not slap_on
        
cv2.destroyWindow("preview")
cv2.waitKey(20) 



