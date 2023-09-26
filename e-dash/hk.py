# # -*- coding: utf-8 -*-
# """
# Created on Fri Aug 23 11:33:10 2019

# """

# from hikvisionapi import Client
# import cv2
# import time
# import pickle

# cam = Client('http://172.16.32.202', 'admin', '12345678#', timeout=30)
# cam.count_events = 2 # The number of events we want to retrieve (default = 1)
# response = cam.Streaming.channels[102].picture(method='get', type='opaque_data')
# with open('screen.jpg', 'wb') as f:
#     for chunk in response.iter_content(chunk_size=1024):
#         if chunk:
#             f.write(chunk)
# # 
# time.sleep(1)
# img = cv2.imread('screen.jpg')
# file='ipimg'
# of=open(file,'wb')
# pickle.dump(img,of)
# of.close()
# cv2.imwrite('ip.jpg',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()