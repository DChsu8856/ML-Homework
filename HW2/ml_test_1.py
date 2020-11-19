# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 23:02:31 2020

@author: jerry
"""


"""
The template of the main script of the machine learning process
"""

import random
import pickle
import numpy as np
import pickle
import numpy as np
from os import listdir
from os.path import isfile, join

ball_postition_history=[]

class MLPlay:
    def __init__(self):
        """
        Constructor
        """
        self.ball_served = False

        
            
    def update(self, scene_info):
        
        filename="C:\\Users\\jerry\\MLGame-master\\games\\arkanoid\\ml\\svr_example.sav"
        model=pickle.load(open(filename, 'rb'))
        
        random_left_right = random.randint(0,99)%2
        ball_center = scene_info["ball"][0]+2.5
        ball_height = scene_info["ball"][1]
        platform_center = scene_info["platform"][0]+20
        """
        Generate the command according to the received `scene_info`.
        """
        ball_postition_history.append(scene_info["ball"])
        ###print(len (ball_postition_history))
        
        if(len (ball_postition_history) > 1):
            vx=ball_postition_history[-1][0]-ball_postition_history[-2][0]
            vy=ball_postition_history[-1][1]-ball_postition_history[-2][1]
            inp_temp = np.array([scene_info["ball"][0], scene_info["ball"][1], scene_info["platform"][0],vx,vy])
            input = inp_temp[np.newaxis, :]
        
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER"):
            return "RESET"
        elif(scene_info["status"] == "GAME_PASS"):
            return "RESET1"
        
        elif not self.ball_served:
            self.ball_served = True
            
            if random_left_right == 0:
                command = "SERVE_TO_LEFT"
            else:
                command = "SERVE_TO_RIGHT"
            
        else:
           ### command = "NONE"
            if (len(ball_postition_history) > 1):
                move = model.predict(input)     
            else:
                move = 0
                
        # 3.4. Send the instruction for this frame to the game process
            if move < 0:
                ###comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                command = "MOVE_LEFT"
            elif move > 0:
               ###comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
               command = "MOVE_RIGHT"
            else:
                ###comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                command = "NONE"

        return command
        


    def reset(self):
        self.ball_served = False

    def reset1(self):
        """
        Reset the status
        """
        self.ball_served = False
        path = 'C:\\Users\\jerry\\MLGame-master\\games\\arkanoid\\log'
        Frame = []
        Status = []
        BallPosition = []
        PlatformPosition = []
        Brick = []
        n=0
        files = listdir(path)    ## import os 取路徑底下檔名


        for f in files:         ##將路徑底下的檔名與路徑結合
            allpath = join(path, f)
            if isfile(allpath):
                with open(allpath , "rb") as f1:
        
                        data_list1 = pickle.load(f1)     
                        for ml_name in data_list1.keys():
                            if ml_name == "record_format_version":
                                continue

                target_record = data_list1[ml_name]
                for n in range(0,len(target_record["scene_info"])):
                    BallPosition.append(target_record["scene_info"][n]["ball"])
                    PlatformPosition.append(target_record["scene_info"][n]["platform"])
                    Frame.append(target_record["scene_info"][n]["frame"])
                    Status.append(target_record["scene_info"][n]["status"])
                    Brick.append(target_record["scene_info"][n]["bricks"])

###############################################################################
        PlatX = np.array(PlatformPosition) [:,0][:,np.newaxis]
        PlatX_next = PlatX[1:,:]
        instrust = (PlatX_next-PlatX[0:len(PlatX_next),0][:,np.newaxis])/5

        PlatY = np.array(PlatformPosition) [:,1][:,np.newaxis]
        PlatY_next = PlatY[1:,:]

        Ballarray = np.array(BallPosition[:-1])

        BallX_position = np.array(BallPosition)[:,0][:,np.newaxis]
        BallX_position_next = BallX_position[1:,:]
        Ball_Vx = BallX_position_next - BallX_position[0:len(BallX_position_next),0][:,np.newaxis]

        BallY_position = np.array(BallPosition)[:,1][:,np.newaxis]
        BallY_position_next = BallY_position[1:,:]
        Ball_Vy = BallY_position_next - BallY_position[0:len(BallY_position_next),0][:,np.newaxis]
        
        Ball_Plat_Y = PlatY_next-BallY_position_next

        x = np.hstack((Ballarray,PlatX[0:-1,0][:,np.newaxis],Ball_Vx,Ball_Vy))
        print(x)

        y = instrust
#np.set_printoptions(threshold=np.inf)
#--------------------------- train & test data
        from sklearn.model_selection import train_test_split
        x_train,x_test,y_train,y_test = train_test_split(x,y,test_size = 0.2,random_state = 41)
#--------------------------- train model
        from sklearn.svm import SVR
        svr = SVR(gamma=0.001,C = 1,epsilon = 0.1,kernel = 'rbf')
        svr.fit(x_train,y_train)
        y_predict = svr.predict(x_test)
        from sklearn.metrics import r2_score#R square
        R2 = r2_score(y_test,y_predict)
        print('R2 = ',R2)
        print(len(Frame))
#--------------------------- save
        filename = "C:\\Users\\jerry\\MLGame-master\\games\\arkanoid\\ml\\svr_example.sav"
        pickle.dump(svr,open(filename,"wb"))
