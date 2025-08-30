"""
Khang Nguyen
March 18 2024
MasterGUI
IST
"""
#Importing DB, TK, and  other libaries.
from tkinter import FLAT, filedialog, messagebox
import tkinter as tk
import os, sys
import time
import string
import random
import datetime as dt
from tkinter import ttk
from openai import OpenAI
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from MasterDB import *
import requests
from io import BytesIO
from PIL import Image
from PIL import ImageTk
import threading
from gtts import gTTS
import pygame

#Creating GUI class.
class GUI:

    #Defining init, contains all buttons, labels, etc.
    def __init__(self):

        #Creating tk window.
        mainWin = tk.Tk()
        self.mainWin = mainWin
        self.mainWin.config(bg="lightgreen")
        mainWin.geometry("800x680")
        mainWin.resizable(False, False)
        mainWin.title("AI ChatBot")

        #CHanging the tk window icon.
        icon_image = tk.PhotoImage(file="aiAvatar.png")
        mainWin.iconphoto(True, icon_image)

        #Instantiating my db.
        self.dbObj = dbConnector()

        #Making my menu.
        self.btnMenu = tk.Menu(mainWin)

        #declaring a vraiable for alter uses/
        self.previousPosition = 0

        #Making a Frame at the center.
        self.centerFrame = tk.Frame(mainWin, relief="solid", borderwidth=1, bg="white", width=600, height=700)
        self.centerFrame.place(y=0, x=100)

        #First menu dropdown, file.
        self.fileMenu = tk.Menu(self.btnMenu, tearoff=0)
        self.fileMenu.add_command(label="Delete File", command=self.deleteCon)
        self.fileMenu.add_command(label="Exit", command=mainWin.quit)
        self.btnMenu.add_cascade(menu=self.fileMenu, label="File")


        #MenuButton, connection toggle.
        self.connectionButton = tk.Menubutton(self.btnMenu)
        self.btnMenu.add_cascade(menu=self.connectionButton, label="Connect",  command=self.connectionToggle)

        #Second menu dropdown, Theme.
        self.helpMenu = tk.Menu(self.btnMenu, tearoff=0)
        self.helpMenu.add_command(label="About", command=self.aboutBox)
        self.helpMenu.add_command(label="Help", command=self.helpBox)
        self.btnMenu.add_cascade(menu=self.helpMenu, label="Help")

        #Creating and placing all of the main buttons and labels (Inside the centerFrame).
        self.questionInput = tk.Entry(self.centerFrame, text="Enter a question......", width=80, highlightbackground="black",highlightcolor="black", highlightthickness=2)
        self.questionInput.place(x=25,y=519)

        self.submitButton = tk.Button(self.centerFrame, text=">", width=6, bg="lightgreen", command=lambda: self.submitQuestion(event), fg="black")
        self.submitButton.place(x=525, y=518)

        self.userDialouge = tk.Text(self.centerFrame, width=50, height=8, highlightbackground="black",bg="lightgreen", highlightthickness=1, fg="black")
        self.userDialouge.place(x=80, y=125)

        self.userDate = tk.Label(self.centerFrame, width=20, height=1, text="", fg="black", highlightbackground="black",bg="lightgreen", highlightthickness=1)
        self.userDate.place(x=80, y=90)

        self.avatarImg = tk.PhotoImage(file='defaultAvatar.png')
        self.resize_avatarImg = self.avatarImg.subsample(12,12)
        
        self.userAvatar= tk.Button(self.centerFrame, image=self.resize_avatarImg, command= self.dummyMethod,borderwidth=0, highlightthickness=0)
        self.userAvatar.place(x=500, y=100)

        self.aiDialouge = tk.Label(self.centerFrame, width=56, height=8, highlightbackground="black",bg="lightgreen", highlightthickness=1, fg="black", wraplength=400)
        self.aiDialouge.place(x=120, y=350)

        self.aiDate = tk.Label(self.centerFrame, width=20, height=1, text="", fg="black", highlightbackground="black",bg="lightgreen", highlightthickness=1)
        self.aiDate.place(x=375, y=310)

        self.avatarImg_ai = tk.PhotoImage(file='aiAvatar.png')
        self.resize_aiImg = self.avatarImg_ai.subsample(3,3)
        
        self.aiAvatar= tk.Button(self.centerFrame, image=self.resize_aiImg, command= self.dummyMethod,borderwidth=0, highlightthickness=0)
        self.aiAvatar.place(x=20, y=320)



        #Making and placing framees, buttons, and labels.
        self.topicLabel = tk.Label(self.mainWin, width=80, text="TOPIC", highlightbackground="black", highlightthickness=2, fg="black", wraplength=300)
        self.topicLabel.place(x=110,y=10)

        self.durationLabel = tk.Label(self.centerFrame, width=60, text="", bg="lightgreen", highlightbackground="black", highlightthickness=2, fg="black", wraplength=300)
        self.durationLabel.place(x=60,y=566)

        #Makigna frame for the bottom.
        self.bottomframe = tk.Frame(mainWin, relief="solid", borderwidth=1, bg="grey", width=500)
        self.bottomframe.place(y=588, x=-3)

        #Making and placing all the buttons and label inside bottom frames.
        self.maxBackbutton = tk.Button(self.bottomframe, text="|<",width=6, height=2, command=self.backConMax)
        self.maxBackbutton.place(x=67,y=8)

        self.skipBackbutton = tk.Button(self.bottomframe, text="<<",width=6, height=2, command=self.backCon3)
        self.skipBackbutton.grid(row=0,column=1,padx=11,pady=8)

        self.backButton = tk.Button(self.bottomframe, text="<",width=6, height=2, command=self.backCon)
        self.backButton.grid(row=0,column=2,padx=11,pady=8)

        self.forwardButton = tk.Button(self.bottomframe, text=">",width=6, height=2, command=self.nextCon)
        self.forwardButton.grid(row=0,column=3,padx=11,pady=8)

        self.skipForwardButton = tk.Button(self.bottomframe, text=">>",width=6, height=2, command=self.nextCon3)
        self.skipForwardButton.grid(row=0,column=4,padx=11,pady=8,)

        self.maxForwardButton = tk.Button(self.bottomframe, text=">|",width=6, height=2, command=self.nextMax)
        self.maxForwardButton.grid(row=0,column=5,padx=11,pady=8)

        self.updateLabel = tk.Button(self.bottomframe, text="Update", width=6, height=2, command=self.updateToggle)
        self.updateLabel.grid(row=0,column=7,padx=11,pady=8)

        self.deleteButton = tk.Button(self.bottomframe, text="Delete",width=6, height=2, command=self.deleteDialouge)
        self.deleteButton.grid(row=0,column=8,padx=11,pady=8)
        
        self.newButton = tk.Button(self.bottomframe, text="New Conversation",width=15, height=2, command=self.createTb)
        self.newButton.grid(row=0,column=9,padx=11,pady=8)

        self.Label = tk.Label(self.bottomframe, width=15, height=20, bg="grey")
        self.Label.grid(row=1,column=0,padx=11,pady=8)

        #Status label that returns any error using try and excepts.
        self.statusLabel = tk.Label(self.bottomframe, text="Status: N/A",width=100, height=2,bg="grey", fg="black", font=(0,7), wraplength=1000)
        self.statusLabel.place(x=80, y=56)

        #Creating a canvas and then creating my scroll bar used to change the ID for my center frame.
        canvasWidth = -10
        self.scrollCanvas = tk.Canvas(self.mainWin, width=canvasWidth)
        self.scrollCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.FALSE)

        #Making the a frame that hold a bunch of random object which attaches to the scroll bar allowing it to actually scroll.
        #THis is due to the fact that the center frame doesn't actually move. Meaning we create a substitude.
        self.scrollFrame = tk.Frame(self.scrollCanvas)

        #Anchoring the area North West or the top left cornor.
        self.scrollCanvas.create_window((0, 0), window=self.scrollFrame, anchor=tk.NW)

        #Writing into the scrollFRame a 100 numbers that extends it beyond the size of the window allow the scroll abr to function.
        for i  in range(100):
            self.scrollLabel = tk.Label(self.scrollFrame,text=str(i))
            self.scrollLabel.pack(fill=tk.X)
        
        #Makign the actual scrollbar.
        self.scrollBar = tk.Scrollbar(mainWin, orient=tk.VERTICAL)
        self.scrollBar.pack(side=tk.RIGHT, fill=tk.Y)

        #Assigning the scrollBar and scrollCanvas to functions that allow them to work.
        self.scrollBar.config(command=self.scrollCanvas.yview)
        self.scrollCanvas.config(yscrollcommand=self.scrollBar.set)

        #Binding the scrollBar to a left click detection function. ANd to call a method everytime it detect the mouse left clicking and moving.
        self.scrollBar.bind("<B1-Motion>", self.onScroll)

        #Binding the scroll frame to that if the frame size is change or configure, is calls a method.
        self.scrollFrame.bind("<Configure>", self.update_scroll_region)

        #Binding the entry to a return  bind, which calls the submit method if the user click the enter key while focused on the entry.
        self.questionInput.bind("<Return>", self.submitQuestion)


        #Configuring the btnMenu to show up.
        mainWin.config(menu=self.btnMenu)

        #Setting variables and booleans.
        self.boolConnect=False
        self.conversationLen = 0
        self.currentIndex = 0
        self.tb_Id = 0
        self.updateBool = False
        event = ""
        self.url = ""
        self.imgDescription = ""

        #Making the loading frame to hold my progress bar.
        self.loading_frame = tk.Frame(self.mainWin, relief="solid", borderwidth=1)
        self.loading_frame.place(x=180,y=250)
        
        self.progress = ttk.Progressbar(self.loading_frame, mode='determinate', length=400)
        self.progress.pack(pady=20, padx=20)

        #Making a label to go along with the loading bar.
        self.loading_label = tk.Label(self.loading_frame, text="Loading...", font=("Arial", 12))
        self.loading_label.pack(pady=5)

        #Calling the stop load so that it hides the loading bar when the program start.
        self.stopLoad()

        #Creating the frame for the right tab.
        self.tabRight = tk.Frame(self.mainWin)
        self.tabRight.place(x=0,y=0)
        self.tabRight.config(width=20)

        #Creating and griding all the button inside the frame and assigning them their function.
        self.readBtn = tk.Button(self.tabRight, text="Read", command=self.speech, highlightthickness=0, bd=0, relief="flat")
        self.readBtn.grid(row=0,column=0, padx=4, pady=2)
        self.copyBtn = tk.Button(self.tabRight, text="Copy", command=self.copy, highlightthickness=0, bd=0, relief="flat")
        self.copyBtn.grid(row=1,column=0, padx=4, pady=2)
        self.pasteBtn = tk.Button(self.tabRight, text="Paste", command=self.paste, highlightthickness=1, bd=0, relief="flat")
        self.pasteBtn.grid(row=3,column=0, padx=4, pady=2)

        #Assigning the main window the binding of right click or left, which they check for certain requriement to check the full function.
        self.mainWin.bind("<Button-3>", self.rightClick)
        self.mainWin.bind("<Button-1>", self.leftClick)

        #Giving all the buttons inside the tabRight frame a hover enffect by giving them the binding of both leave and enter.
        self.readBtn.bind("<Enter>", self.hoverOn)
        self.readBtn.bind("<Leave>", self.hoverOut)
        self.copyBtn.bind("<Enter>", self.hoverOn2)
        self.copyBtn.bind("<Leave>", self.hoverOut2)
        self.pasteBtn.bind("<Enter>", self.hoverOn3)
        self.pasteBtn.bind("<Leave>", self.hoverOut3)

        #Creating some variable and booleans to be used.
        self.tab = False
        self.selected_text = "hello"
        self.right = False

        #Instantiating/calling the pygame init.
        pygame.init()

        #Calling the forget method to forget/hide the tabRight frame at the start of the frame.
        self.forget()

        #Adding a copy text and read text function to the AI label. ALlowing the user to copy the ai text or reading it out loud.
        audioPil = Image.open(r"C:\Users\khang\Desktop\IST\IST Work\Python\audio.png")

        size = (30, 20)
        resized_audio = audioPil.resize(size, resample=Image.LANCZOS)

        audio_img = ImageTk.PhotoImage(resized_audio)
        
        self.audioAI = tk.Button(self.centerFrame, image=audio_img, command=self.readAI, highlightthickness=0, bd=0, relief="flat")
        self.audioAI.place(x=320, y=310)


        copyPil = Image.open(r"C:\Users\khang\Desktop\IST\IST Work\Python\copy-icon.png")

        resized_copy = copyPil.resize(size, resample=Image.LANCZOS)

        copy_img = ImageTk.PhotoImage(resized_copy)
        
        self.copyAI = tk.Button(self.centerFrame, image=copy_img, command=self.copyAI_func, highlightthickness=0, bd=0, relief="flat")
        self.copyAI.place(x=280, y=310)


        #Making the sideTab.
        self.sideTab = tk.Frame(self.mainWin, bg='#040404', width=63, height=588)
        self.sideTab.place(x=0, y=0)

        #Making a home icon and the edit icon, then resizing it to fit.
        homePil = Image.open(r"C:\Users\khang\Desktop\IST\IST Work\Python\homeICON.png.png")

        size2 = (48,50)
        resized_Home = homePil.resize(size2, resample=Image.LANCZOS)

        home_img = ImageTk.PhotoImage(resized_Home)

        editPil = Image.open(r"C:\Users\khang\Desktop\IST\IST Work\Python\ediditorIcon.png.png")

        size2 = (48,50)
        resized_edit = editPil.resize(size2, resample=Image.LANCZOS)

        edit_img = ImageTk.PhotoImage(resized_edit)

        #Making all the buttons inside my side tab and
        self.homeBtn = tk.Button(self.sideTab, relief='flat', image=home_img, bg="#040404")
        self.homeBtn.grid(row=0, column=0, pady=7)

        #Assigning img to a button.
        self.editIcon = tk.Button(self.sideTab, relief='flat', image=edit_img, bg="#040404", command=self.editWin)
        self.editIcon.grid(row=1, column=0, pady=10)

        #Making all the button for the sideTab
        self.EditLabel = tk.Button(self.sideTab, text="", bg="#040404", width=10, fg="white", font=(0, 16), command=self.editWin, bd=0, relief='flat')
        self.homeLabel = tk.Label(self.sideTab, text="", bg="#040404", width=5, fg="white", font=(0, 21))
        self.conButton = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch)
        self.conButton1 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch1)
        self.conButton2 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch2)
        self.conButton3 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch3)
        self.conButton4 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch4)
        self.conButton5 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch5)
        self.conButton6 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch6)
        self.conButton7 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch7)
        self.conButton8 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch8)
        self.conButton9 = tk.Button(self.sideTab, text="", relief='flat', bg="#040404", fg="white", font=(0, 10), command=self.conSwitch9)

        #BInding the sideTab to a enter and leave bind, so when the mouse hover in or out of the sideTab is contract or expands.
        #They also uses a lambda function because both the method expand and contract requires a extra variable to be pass.
        self.sideTab.bind('<Enter>', lambda e: self.expand())
        self.sideTab.bind('<Leave>', lambda e: self.contract())

        #Frame often auto size to the object inside the frame, but propagate allow us to force the frames to be a certian size.
        self.sideTab.grid_propagate(False)

        #Creating a min and amx width for the sideTab to extend or contract to.
        self.minWidth = 65
        self.maxWidth =  200 
        self.cur_width = self.minWidth 

        #Making a boolean that track if the tab is current epanded or contracted.
        self.expanded = False 
        
        #Calling 999.
        self.mainWin.mainloop()


    def dummyMethod(self):
        pass
    
    #Messageboxes for the help and about buttons for the menu bar.
    def helpBox(self):
        messagebox.showinfo(title="Help", message="If you are experiencing an issue with the programs. Make sure you have click connect, make sure you are connected to the wifi, and mySQL downloaded on your computer. If your still experiencing issue with the program; You can reach out to a IT support memember on our website 'openai.com'.")
    
    def aboutBox(self):
        messagebox.showinfo(title="ABout", message="You are currently using a late model of openAI chat bot. The model this program use for text generation is 3.5 Turbo. For image generation we make use of openAI dalle-e 3. For image variation generator we make use of the dall-e 2.")
    
    #places the audio and copy button when calls.
    def copy_audioShow(self):
        self.copyAI.place(x=280, y=310)
        self.audioAI.place(x=320, y=310)

    #Hides the copy and audio button when calls.
    def copy_audioHide(self):
        self.copyAI.place_forget()
        self.audioAI.place_forget()

    #Creating the hover and in and out for each of button side rightTab frame.
    def hoverOn(self,event):
        self.readBtn.config(bg="grey", fg="white")


    def hoverOut(self,event):
        self.readBtn.config(bg="white", fg="black")


    def hoverOn2(self,event):
        self.copyBtn.config(bg="grey", fg="white")


    def hoverOut2(self,event):
        self.copyBtn.config(bg="white", fg="black")


    def hoverOn3(self,event):
        self.pasteBtn.config(bg="grey", fg="white")


    def hoverOut3(self,event):
        self.pasteBtn.config(bg="white", fg="black")

    #Forget/hides the rightTab when calls.
    def forget(self):
        self.tabRight.place_forget()

    #place the rightTab as the assign variable.
    def remember(self,x,y):
        self.tabRight.place(x=x,y=y)

    #Start the loading animation.
    def startLoad(self):
        self.loading_frame.place(x=180,y=250)

        self.progress.start(20)
        self.animateLoad()

    #Animates the loading label when the loading animation is called.
    def animateLoad(self):
        self.loading_label.config(text=self.loading_label.cget("text") + ".") 
        if (len(self.loading_label.cget("text")) > 12):
            self.loading_label.config(text="Loading")
        self.mainWin.after(500, self.animateLoad)
    
    #Stops the loading animations
    def stopLoad(self):
        self.progress.step(100)
        self.progress.stop()
        time.sleep(0.5)
        self.loading_frame.place_forget()

    #THe connection metod. COnnects you the databse based on a toggle/booleans.
    def connectionToggle(self):
        try:

            #If bool is true then it disconnects you the database and chang ethe label to connect.
            if (self.boolConnect):
                self.btnMenu.entryconfig(index=2,label="Connect")
                self.dbObj.disconnect()
                self.boolConnect = False
                self.statusLabel.config(text="Status: You have DISCONNECTED from the database.")

            #If bool is false then it connects you to the database and change the label to disconnect.
            else:
                self.btnMenu.entryconfig(index=2,label="Disconnect")
                self.dbObj.connection()
                self.boolConnect=True
                self.load(self.currentIndex)
                self.statusLabel.config(text="Status: You have CONNECTED from the database.")

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    def submitQuestion(self, event):
        try:
            self.startLoad()

            userQuestion = str(self.questionInput.get())

            # If the user's question is blank, it will stop loading.
            if (userQuestion == ""):
                self.stopLoad()
                return None
            
            #If it is not empty then it will calls the method and continue the submit method.
            else:
                self.submit(userQuestion)
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
        finally:
            self.fill()

    #The continued submit method.
    def submit(self, userQuestion):

        #Reading the tb list and find the current table to get the list of items from that table.
        tb_List = self.dbObj.readTb()
        current_tb = tb_List[self.tb_Id][1]
        db_List = self.dbObj.readAll(current_tb)

        #Finding the max Id.
        db = len(db_List) - 1
        maxId = db

        #If the user entry has anything about generating an image, then call the generate image method.
        if ("generate image" in userQuestion.lower() or "generate photo" in userQuestion.lower() or "generate an image" in userQuestion.lower()):
            image_thread = threading.Thread(target=self.generateImage, args=(userQuestion,))
            image_thread.start()

        #Else calls the generate text method.
        else:
            text_thread = threading.Thread(target=self.generateText, args=(userQuestion,))
            text_thread.start()

        #Setting the current index to the max Id.
        self.currentIndex = maxId
    
    #Generates text by open ai method.
    def generateText(self, userQuestion):
        try:
            #CLears the entry box.
            self.questionInput.delete(0, tk.END)

            #Insert the user query into the user dialogue.
            self.userDialouge.delete("1.0", tk.END)
            self.userDialouge.insert(tk.END , userQuestion)

            #Calls the ai generate method by putting in the user prompt to get back text from the ai.
            ai_list = self.aiGeneration(userQuestion)
            ai_response = ai_list[0]

            #Removing the unwanted part of the ai generated text.
            ai_str = str(ai_response)
            ai_new = ai_str.replace("role='assistant', function_call=None, tool_calls=None)",'')
            ai_final = ai_new.replace('ChatCompletionMessage(content=', '')

            #Putting the ai text into the ai dialogue.
            self.aiDialouge.config(text=ai_final, image="",  width=56, height=8)
            self.aiDialouge.place(x=120, y=350)

            #Finding the date and time of when the user submit their query.
            date = dt.datetime.now()
            self.userDate.config(text=f"{date:%A, %B %d, %Y}")
            self.aiDate.config(text=f"{date:%A, %B %d, %Y}")
            self.aiDate.place(x=375, y=310)

            #SUmmarizing the ai chat responds into a shorter responds for the topic sentence.
            message_content = ai_list[1]
            self.summary = self.summarizeTx(message_content)

            self.topicLabel.config(text="Topic: {}".format(self.summary))

            #Getting the max Id to assign it to conversation Lenght.
            tb_List = self.dbObj.readTb()
            current_tb = tb_List[self.tb_Id][1]
            db_List = self.dbObj.readAll(current_tb)
            db = len(db_List) - 1
            maxId = db

            if (maxId is None):
                self.conversationLen = 1
            else:
                self.conversationLen = int(maxId)

            #Assigns the conversation lenght labe; the term st, nd, rd, or th based upon the number.
            if (self.conversationLen == 1):
                self.durationLabel.config(text="This the {}st dialouges" .format(self.conversationLen))

            if (self.conversationLen == 2):
                self.durationLabel.config(text="This the {}nd dialouges" .format(self.conversationLen))

            if (self.conversationLen == 3):
                self.durationLabel.config(text="This the {}rd dialouges" .format(self.conversationLen))

            if (self.conversationLen > 3):
                self.durationLabel.config(text="This the {}th dialouges" .format(self.conversationLen))
            
            #Shows the copy and audio buttons by calling this method.
            self.copy_audioShow()

            #Inserts everything into the databse by calloing the insert method.
            self.insertDialogues(self.tb_Id, date, self.conversationLen)

            #Stops the load.
            self.stopLoad()

        except Exception as error:
            self.stopLoad()
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #THis method insert everything into the db table.
    def insertDialogues(self, tb_Id, date, duration):
        try:
            
            #FInds the current table the user is looking at.
            tb_List = self.dbObj.readTb()
            current_tb = tb_List[tb_Id][1]

            #Gets everything needed from the labels and text boxes.
            user = self.userDialouge.get("1.0", "end-1c")
            ai = self.aiDialouge.cget("text")
            topic = self.topicLabel.cget("text")
            
            #Calls the db objects to insert into the db table.
            self.dbObj.createDialouge(user, ai, date, topic, duration, current_tb)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The delete method. WHen calls ask the user if they want to delete the current dialogues.
    def deleteDialouge(self):
        try:
            summary = self.topicLabel.cget("text")
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete this dialouge where {}?" .format(summary))

            if (confirm):
                #If the user click yes, then call the actual delete method.
                self.confirmDelete()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

        finally:
            #Calls the fill method which refresh the sideTab.
            self.fill()

    #The actual delete method.
    def confirmDelete(self):
        try:

            #Find the current table the user looks out.
            tb_list = self.dbObj.readTb()
            current_tb = tb_list[self.tb_Id][1]

            if (current_tb):

                #Get the text from the user dialogue.
                entry = self.userDialouge.get("1.0", "end-1c")

                #Calls the db object to delete from the current table.
                self.dbObj.deleteDialouge(entry, current_tb)

                #Calls the load method.
                self.load(self.currentIndex)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The delete conversation method. Ask the user if theyw ant to delete the entire table their currently on.
    def deleteCon(self):
        try:
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete this Conversation where index = {}?" .format(self.tb_Id))

            #IF the user say yes, then calls the actual delete method.
            if (confirm):
                self.confirmDeleteCon()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

        finally:
            self.fill()

    #The actual delete conversation method.
    def confirmDeleteCon(self):
        try:

            #FIn ds the current table the user is on.
            tb_list = self.dbObj.readTb()
            current_tb = tb_list[self.tb_Id][1]

            if (current_tb):

                #Calls the delete method from the db class.
                self.dbObj.deleteConDB(current_tb)
                
                #Calls the load methodd.
                self.load(self.currentIndex)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The new table method. Creates a new table and add it into the database.
    def createTb(self):
        try:

            #Calls the name generator to generate and random name.
            tb = self.nameGenerator()

            #Calls the insert table name. To add the table name into the table dictionaries to be use later.
            self.dbObj.insertTb_Name(tb)

            #Finds the max Id.
            tb_list = self.dbObj.readTb()
            maxTb = len(tb_list)
            self.tb_Id = maxTb - 1

            #Calls the db class to actually create the table if not already existing.
            self.dbObj.new_Conversation(tb)

            #Clears everything.
            self.userDialouge.delete("1.0",tk.END)

            self.aiDialouge.config(text="")
            self.aiDate.config(text="")
            self.userDate.config(text="")
            self.topicLabel.config(text="")
            self.durationLabel.config(text="")

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #AN update toggle method. Checks the update booleans to either call the update mehtod or change the label to commit.
    def updateToggle(self):
        if (self.updateBool):
            self.updateLabel.config(text="Update")
            userEntry = self.userDialouge.get("1.0", tk.END)
            self.updateDialogues(userEntry)
            self.updateBool = False

        else:
            self.updateLabel.config(text="Commit")
            self.updateBool=True

    #The actual update method.
    def updateDialogues(self, userEntry):
        try:
            self.startLoad()
            #Checks if the user is generating an image or text.
            if ("generate image" in userEntry.lower() or "generate photo" in userEntry.lower() or "generate an image" in userEntry.lower()):

                #Calls a thread so it doesn't lag any other method like the animate laod.
                image_thread = threading.Thread(target=self.generateImage2, args=(userEntry,))
                image_thread.start()             

            else:
                tx_thread = threading.Thread(target=self.updateDialogue2, args=(userEntry,))
                tx_thread.start()   
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The text update method.
    def updateDialogue2(self, userEntry):
        try:

            #Finds the current id inside the table.
            tb_list = self.dbObj.readTb()
            current_tb = tb_list[self.tb_Id][1]
            db_List = self.dbObj.readAll(current_tb)
            Id = db_List[self.currentIndex][0]

            #Generates the ai responds text by passing through the user entry.
            ai_list = self.aiGeneration(userEntry)
            ai_response = ai_list[0]

            #Replace unwanted part from the ai responds
            ai_str = str(ai_response)
            
            ai_new = ai_str.replace(", role='assistant', function_call=None, tool_calls=None)",'')
            ai_final = ai_new.replace('ChatCompletionMessage(content=', '')

            #FInds the date.
            date = dt.datetime.now()

            #SUmmarize the ai responds.
            message_content = ai_list[1]
            summary = self.summarizeTx(message_content)

            #Calls the updat emethod from the db class.
            self.dbObj.updateDB(userEntry, ai_final, date, summary, current_tb, Id)

            self.load(self.currentIndex)
            self.statusLabel.config(text="Status: You have successfully updated into the database.")

            self.stopLoad()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Just checks the url making sure there is not error.
    def urlChecker(self, url, size, description, userEntry):
        if (url is not None):
            self.mainWin.after(0, self.handleImageGeneration, url, size, description, userEntry)

        else:
            self.statusLabel.config(text="Status: (ERROR) Couldn't generate image; URL is empty.")

    #The load methods.
    def load(self, index):
        
        tb_list = self.dbObj.readTb()

        #Finds the the tb id.
        new_tbId = min(self.tb_Id, len(tb_list))

        self.tb_Id = new_tbId

        #Finds the current table list.
        current_tb = tb_list[new_tbId][1]

        dbList = self.dbObj.readAll(current_tb)

        #If the table is empty clear out all the entry, label, textbox.
        if (not dbList):

            self.userDialouge.delete("1.0", tk.END)

            self.aiDialouge.config(text="", image="")
            self.aiDate.config(text="")
            self.userDate.config(text="")
            self.topicLabel.config(text="")
            self.durationLabel.config(text="")
            return

        len_dbList = len(dbList) - 1

        try:
            #Finds wheter the GUI is tryign  to load a ai iamge generated responds to text generated repsonds.
            new_index = min(index, len_dbList)

            ai = dbList[new_index][2]
            if (ai is not None):
                self.tx_load(ai, dbList, new_index)

            else:
                self.img_load(dbList, new_index)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The iamge laod method.
    def img_load(self, dbList, new_index):
        try:

            #Finds the content for all the columns.
            user = dbList[new_index][1]
            date = dbList[new_index][3]
            topic = dbList[new_index][4]
            duration = dbList[new_index][5]
            img_data = dbList[new_index][6]

            #Reads the blob data/binary data and convert into a picture usuable by tk.
            size = (400,200)

            image = Image.open(BytesIO(img_data)).resize(size, resample=Image.LANCZOS)

            self.userDialouge.delete("1.0", tk.END)
            self.userDialouge.insert(tk.END, user)

            photo_image = ImageTk.PhotoImage(image)
            self.aiDialouge.config(image=photo_image)
            self.aiDialouge.image = photo_image

            self.aiDialouge.place(x=120, y=300)
            self.aiDate.place(x=375, y=270)

            #Inserts everything into the label and text box
            self.aiDialouge.config(width=size[0], height=size[1])
            self.aiDate.config(text=date)
            self.userDate.config(text=date)
            self.topicLabel.config(text=topic)

            if (duration == 1):
                self.durationLabel.config(text="This is the {}st dialogue".format(duration))

            if (duration == 2):
                self.durationLabel.config(text="This is the {}nd dialogue".format(duration))

            if (duration == 3):
                self.durationLabel.config(text="This is the {}rd dialogue".format(duration))

            if (duration >= 3):
                self.durationLabel.config(text="This is the {}th dialogue".format(duration))

            #Hides the copy and read button.
            self.copy_audioHide()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The text load method.
    def tx_load(self, ai, dbList, new_index):
        try:

            #Finds and insert everything into the labels and text boxes.
            user = dbList[new_index][1]
            date = dbList[new_index][3]
            topic = dbList[new_index][4]
            duration = dbList[new_index][5]

            self.userDialouge.delete("1.0", tk.END)
            self.userDialouge.insert(tk.END, user)

            self.aiDialouge.config(text=ai, image="", width=56, height=8)
            self.aiDialouge.place(x=120, y=350)

            self.aiDate.config(text=date)
            self.aiDate.place(x=375, y=310)

            self.userDate.config(text=date)
            self.topicLabel.config(text=topic)

            if (duration == 1):
                self.durationLabel.config(text="This is the {}st dialogue".format(duration))

            if (duration == 2):
                self.durationLabel.config(text="This is the {}nd dialogue".format(duration))

            if (duration == 3):
                self.durationLabel.config(text="This is the {}rd dialogue".format(duration))

            if (duration >= 3):
                self.durationLabel.config(text="This is the {}th dialogue".format(duration))

            #Shows the copy and read buttons
            self.copy_audioShow()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Checks the current position of the scroll bar and comapres it the previous position and either call next or back method.
    def onScroll(self, event):
        try:        
            position = self.scrollBar.get()

            if (position[0] > self.previousPosition):
                self.scrollNext()
            if (position[0] < self.previousPosition):
                self.scrollBack()
            self.previousPosition = position[0]
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The scroll next method. Adds one to the current index.
    def scrollNext(self):
        try:
            tb_list = self.dbObj.readTb()
            current_tb = tb_list[self.tb_Id][1]
            dbList = self.dbObj.readAll(current_tb)
            
            if (self.currentIndex < len(dbList) - 1):
                self.currentIndex += 1
                time.sleep(0.30)

                self.mainWin.after(0, self.load, self.currentIndex)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Subtract ones from the current idnex.
    def scrollBack(self):
        try:
            if (self.currentIndex > 0):
                self.currentIndex -= 1
                time.sleep(0.30)

                self.mainWin.after(0, self.load, self.currentIndex)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
    
    #Making all the next and back method. ALso make the next 3, back 3, back max, forward max.
    #Simply either adding 1 or subtracting 1 or subtracting or adding 3 based upon the method.
    def nextCon(self):
        try:
            tb_list = self.dbObj.readTb()
            if (self.tb_Id < len(tb_list) - 1):
                self.tb_Id +=1
                self.currentIndex = 0
                self.load(self.currentIndex)
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
        
        finally:
            self.fill()

    def nextCon3(self):
        try:
            tb_list = self.dbObj.readTb()

            if (self.tb_Id + 3 < len(tb_list)):
                self.tb_Id += 3
            else:
                self.tb_Id = len(tb_list) - 1

            self.currentIndex = 0
            self.load(self.currentIndex)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}".format(error))
        finally:
            self.fill()

    def nextMax(self):
        try:
            tb_list = self.dbObj.readTb()
            max_id = len(tb_list) - 1

            self.tb_Id = max_id
            self.currentIndex = 0

            self.load(self.currentIndex)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}".format(error))
        finally:
            self.fill()


    def backCon(self):
        try:
            if (self.tb_Id > 0):
                self.tb_Id -=1
                self.currentIndex = 0
                self.load(self.currentIndex)
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

        finally:
            self.fill()

    def backCon3(self):
        try:
            if (self.tb_Id - 3 >= 0):
                self.tb_Id -= 3
            else:
                self.tb_Id = 0

            self.currentIndex = 0
            self.load(self.currentIndex)
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}".format(error))
        finally:
            self.fill()

    def backConMax(self):
        try:
            self.tb_Id = 0
            self.currentIndex = 0
            self.load(self.currentIndex)
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

        finally:
            self.fill()

    #Generates a random string of letter that 12 characters long. Using for rnadom name generator for creating a new table.
    def nameGenerator(self) -> str:
        return "".join(random.choices(string.ascii_uppercase, k=12))

    #he open ai text generation method.
    def aiGeneration(self,question):
                try:
                    #Declaring the client using the api key to acces open ai.
                    client = OpenAI(api_key="<CENSORED_API_KEY>")

                    completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        #Roles of the ai.
                        {"role": "system", "content": "You are a highly intelligent ai chat bot, you will respond to any question or text given to you."},
                        #User query.
                        {"role": "user", "content": question} 
                    ]
                    )

                    #Returning the ai generated responds.
                    return completion.choices[0].message, completion.choices[0].message.content
                except Exception as error:
                    self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

            
    #The ai iamge generation method.
    def imageGenerator(self,question):
        try:
            client = OpenAI(api_key="<CENSORED_API_KEY>")
            
            #Declares the model wanted, and input the user prompt the image.
            response = client.images.generate(
                model="dall-e-3",
                prompt=question,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            #Seperates the iamg eurl and the text description.
            url = response.data[0].url
            tx = response.data[0]

            #Turns them into strings.
            url_str = str(url)
            tx_str = str(tx)

            #Replace unwanted stuff from the description of the image.
            description = tx_str.replace(url_str, '')
            description2 = description.replace("Image(b64_json=None, revised_prompt=", '')
            description3 = description2.replace(", url='')", '')

            return url, description3

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
            return None

    #The load url method simply reads the url from the ai generated responds and make it into a useable image for tk.
    def load_url(self, url, size):
        try:
            #Used a python libary to make a HTTP request  to a make a GET request from the url.
            response = requests.get(url)

            #Access the content from what the url response (Gets the binary data).
            image_data = response.content

            #Opens the bytesIO object by opening bytes data and then finally resizing the image.
            image = Image.open(BytesIO(image_data)).resize(size, resample=Image.Resampling.LANCZOS)


            #Making image a tk compatible image.
            return ImageTk.PhotoImage(image), image_data
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
    
    #The generate iamge method that manage all the data.
    def generateImage(self, userQuestion):
        try:
            self.questionInput.delete(0, tk.END)
            
            self.userDialouge.delete("1.0", tk.END)
            self.userDialouge.insert(tk.END, userQuestion)

            size = (400, 200)

            #Calls the open ai image generation and passes through the prompt.
            list = self.imageGenerator(userQuestion)

            url = list[0]
            description = list[1]

            if (url is not None):
                #After everything, calls the next method in the chain using the main win after function.
                self.mainWin.after(0, self.handleImageGeneration, url, size, description, userQuestion)

            else:
                self.statusLabel.config(text="Status: (ERROR) Could not generate image; The URL is empty.")

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #This methods calls the load url to read the binary data passed from the image generate method.
    def handleImageGeneration(self, url, size, description, userQuestion):
        try:
            photo = self.load_url(url, size)

            #Calls the final image thread.
            self.mainWin.after(0, self.final_imageThread, photo, size, description, userQuestion)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The final part of image generation.
    def final_imageThread(self, photo, size,description, userQuestion):
        try:

            #Inserts into the ai dialogues box with the image and then change the placing of the ai dialogue and date.
            self.aiDialouge.config(image=photo[0])
            self.aiDialouge.image = photo[0]

            self.aiDialouge.place(x=120, y=300)
            self.aiDate.place(x=375, y=270)
            self.aiDialouge.config(width=size[0], height=size[1])

            #Gets the binary data from the pass tuple.
            binary = photo[1]

            #Inserts into the db table by call the method to do the rest.
            self.insert_theRest(description, userQuestion, binary)

            self.stopLoad()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Insert the rest of the text into label and text boxes and inserting the db table.
    def insert_theRest(self,description,userQuestion,binary):
        try:
            self.questionInput.delete(0, tk.END)

            #Finds current table the user is on.
            tb_List = self.dbObj.readTb()
            current_tb = tb_List[self.tb_Id][1]

            #Finds the date.
            date = dt.datetime.now()
            self.userDate.config(text=f"{date:%A, %B %d, %Y}")
            self.aiDate.config(text=f"{date:%A, %B %d, %Y}")

            #Summarize the description.
            self.summary = self.summarizeTx(description)
            
            #Inserting it into the topic label.
            self.topicLabel.config(text="Topic: {}".format(self.summary))

            #Gets the maxId and then assign it to the conversationLen
            db_List = self.dbObj.readAll(current_tb)
            maxId = len(db_List) - 1
            if maxId is not None:
                self.conversationLen = int(maxId)

            else:
                self.conversationLen = 0

            if (self.conversationLen == 1):
                self.durationLabel.config(text="This the {}st dialouges" .format(self.conversationLen))
            if (self.conversationLen == 2):
                self.durationLabel.config(text="This the {}nd dialouges" .format(self.conversationLen))

            if (self.conversationLen == 3):
                self.durationLabel.config(text="This the {}rd dialouges" .format(self.conversationLen))

            if (self.conversationLen > 3):
                self.durationLabel.config(text="This the {}th dialouges" .format(self.conversationLen))
            
            #Hides the copy and audio buttons.
            self.copy_audioHide()

            #Calls the db obj and then img insert method from the db class.
            self.dbObj.img_Insert(userQuestion, date, self.summary, self.conversationLen, current_tb, binary)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
    
    #################
    #HandleImageGeneration2, generateImage2, final_ImageThread2, and update_theRest is the simillar to the original insert, but redesigned to update instead.
    #################
    def handleImageGeneration2(self, url, size, description, userQuestion):
        try:
            photo = self.load_url(url, size)

            self.mainWin.after(0, self.final_imageThread2, photo, size, description, userQuestion)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    def generateImage2(self, userEntry):
        try:
            self.questionInput.delete(0, tk.END)

            self.userDialouge.delete("1.0", tk.END)
            self.userDialouge.insert(tk.END, userEntry)

            size = (400, 200)

            list = self.imageGenerator(userEntry)

            url = list[0]
            description = list[1]

            self.urlChecker(url, size, description, userEntry)   
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    def final_imageThread2(self, photo, size,description, userQuestion):
        try:
            self.aiDialouge.config(image=photo[0])
            self.aiDialouge.image = photo[0]

            self.aiDialouge.place(x=120, y=300)
            self.aiDate.place(x=375, y=270)
            self.aiDialouge.config(width=size[0], height=size[1])

            binary = photo[1]

            self.update_theRest(description, userQuestion, binary)

            self.stopLoad()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
    
    
    def update_theRest(self,description,userQuestion,binary):
        try:
            self.questionInput.delete(0, tk.END)

            tb_List = self.dbObj.readTb()
            current_tb = tb_List[self.tb_Id][1]

            date = dt.datetime.now()
            self.userDate.config(text=f"{date:%A, %B %d, %Y}")
            self.aiDate.config(text=f"{date:%A, %B %d, %Y}")

            self.summary = self.summarizeTx(description)
            
            self.topicLabel.config(text="Topic: {}".format(self.summary))

            tb_List = self.dbObj.readTb()
            current_tb = tb_List[self.tb_Id][1]
            db_List = self.dbObj.readAll(current_tb)
            id = db_List[self.currentIndex][0]
            
            conId = self.durationLabel.cget("text")
            self.conversationLen = int(conId)

            if (self.conversationLen == 1):
                self.durationLabel.config(text="This the {}st dialouges" .format(self.conversationLen))
            if (self.conversationLen == 2):
                self.durationLabel.config(text="This the {}nd dialouges" .format(self.conversationLen))

            if (self.conversationLen == 3):
                self.durationLabel.config(text="This the {}rd dialouges" .format(self.conversationLen))

            if (self.conversationLen > 3):
                self.durationLabel.config(text="This the {}th dialouges" .format(self.conversationLen))
            
            self.copy_audioHide()

            self.dbObj.updateIMG(userQuestion, date, self.summary, self.conversationLen, current_tb, id, binary)
            self.statusLabel.config(text="Status: You have successfully updated into the database.")

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #A toggle method that either shows or hides the rightTab. It is also called everytime the user right clicked.
    def rightClick(self, event): 
        if (self.right == True):

            #If the booleans is true then hide the rightTab.
            self.forget()
            self.right = False

        else:

            #If the booleans is false call the 2nd method.
            self.rightClick2()


    def rightClick2(self):
        try:
            #Check if any text inside th userDIalogue is highlight by checking if an text range is tagged with 'sel'.
            if (self.userDialouge.tag_ranges("sel")):

                #Finds and grabs the first and last character of the highlighted range.
                start = self.userDialouge.index("sel.first")
                end = self.userDialouge.index("sel.last")

                #Grabs all the text between the first and last character.
                self.selected_text = self.userDialouge.get(start, end)

                #Find the x and y position of the cursosr to pass through the remember method to be alter used.
                cursor_x = self.mainWin.winfo_pointerx() - self.mainWin.winfo_rootx()
                cursor_y = self.mainWin.winfo_pointery() - self.mainWin.winfo_rooty()

                #Calls the remember method and set all required bool.
                self.remember(cursor_x, cursor_y)
                self.tab = True
                self.right = True

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #A toggle of left click button. It basically if the the rightTab opened or not.
    def leftClick(self, event):
        #If the rightTab is open call the 2nd part.
        if (self.tab == True):
            self.leftClick2()

        else:
            return None

    def leftClick2(self):
        try:

            #Finds the cursor position.
            x = self.mainWin.winfo_pointerx() - self.mainWin.winfo_rootx()
            y = self.mainWin.winfo_pointery() - self.mainWin.winfo_rooty()

            #Find the x and y coordinate of the top left cornor of the tabRight frame.
            frame_x = self.tabRight.winfo_rootx() - self.mainWin.winfo_rooty()
            frame_y = self.tabRight.winfo_rooty() - self.mainWin.winfo_rooty()

            #Finds the height of the tabRight window.
            frame_width = self.tabRight.winfo_width()
            frame_height = self.tabRight.winfo_height()

            #If the user left clicks while the window is open. Check if the user left clicked outside the the frame by check if x or y is less or greater than the min or max of the height and width.
            if (x <= frame_x - 20 or x >= frame_x + frame_width + 20 or y <= frame_y - 20 or y >= frame_y + frame_height + 20):
                self.forget()
                self.tab = False

            else:
                return None
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
    
    #Read method that turns text to speech.
    def speech(self):
        try:

            #Sets the language.
            language = 'en'

            #Grab the text selected.
            text = self.selected_text
            
            #Uses the gTTS libary to download the text and turn it into speecha nd stored in a mp3 file.
            speech = gTTS(text=text, lang=language, slow=False)
            speech.save("welcome.mp3")

            #Uses the pygame libary to run the mp3 file.
            audio = pygame.mixer.Sound('welcome.mp3')
            
            audio.play()
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
        
    #Copy text method.
    def copy(self):
        try:

            #Check if anything is highlighted.
            if (self.userDialouge.tag_ranges("sel")):

                #Gets the first and last character.
                start = self.userDialouge.index("sel.first")
                end = self.userDialouge.index("sel.last")

                #Get the text between the first and last character.
                selected_text = self.userDialouge.get(start, end)

                #Use the clipboard method to clear the user copy adn paste and then append/add the selected text to the clipboard.
                self.mainWin.clipboard_clear()
                self.mainWin.clipboard_append(selected_text)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The paste method.
    def paste(self):
        try:

            #Grabs the text stored in the clipboard.
            copied_text = self.mainWin.clipboard_get()

            #Insert it into the userDialogue.
            self.userDialouge.insert(tk.INSERT, copied_text)
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
    
    #Does the same thing but copies the ai dialogue.
    def copyAI_func(self):
        try:
            tx = self.aiDialouge.cget("text")

            self.mainWin.clipboard_clear()
            self.mainWin.clipboard_append(tx)
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Does the same thing as the read method but reads the ai dialogue.
    def readAI(self):
        try:
            language = 'en'

            text = self.aiDialouge.cget("text")
            
            speech = gTTS(text=text, lang=language, slow=False)
            speech.save("welcome.mp3")

            audio = pygame.mixer.Sound('welcome.mp3')
            
            audio.play()
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The expand method.
    def expand(self):
        try:
            #Increase the current width.
            self.cur_width += 10

            #Calls expand again after the method is finish.
            #This allows for a smooth animation.
            rep = self.mainWin.after(5, self.expand)

            #Set the width of the sideTab to the current width.
            self.sideTab.config(width=self.cur_width) 

            #IF the current width is not bigger then the max width. Keep repeating the expand method. 
            if (self.cur_width >= self.maxWidth): 

                self.expanded = True
                self.mainWin.after_cancel(rep)  

                #Calls fill to refresh the buttons.
                self.fill()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Does the same thing as the expand method but -10 for current width.
    def contract(self):
        try:
            self.cur_width -= 10 

            rep = self.mainWin.after(5, self.contract)  
            self.sideTab.config(width=self.cur_width)

            if (self.cur_width <= self.minWidth):
                self.expanded = False 
                self.mainWin.after_cancel(rep)
                 
                self.fill()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Depending on the if the sideTab is expanded or not (by checking a bool).
    #Hides or show the main labels and buttons.
    def fill(self):
        if (self.expanded): 

            #Showing the buttons and labels if true.
            self.homeLabel.config(text="Hello!")
            self.homeLabel.place(x=60, y=15)

            self.EditLabel.config(text="Image Editor")
            self.EditLabel.place(x=53, y=88)

            #Loading all the buttons.
            self.sideBtn_Load()

        else:

            #Hiding all the buttons.
            self.EditLabel.place_forget()
            self.conButton.place_forget()
            self.homeLabel.place_forget()
            self.conButton1.place_forget()
            self.conButton2.place_forget()
            self.conButton3.place_forget()
            self.conButton4.place_forget()
            self.conButton5.place_forget()
            self.conButton6.place_forget()
            self.conButton7.place_forget()
            self.conButton8.place_forget()
            self.conButton9.place_forget()

    #######################
    #This section check the if a certain row is null or is storing content.
    #If the assigned button row is not empty it shows the button and calls the next method.
    #Then the next method does same and it is a chain for 10 buttons in a row.
    #If a row is empty, then it stop the chain assuming there is nothign after the empty row.
    #######################
    def sideBtn_Load(self):
        try:
            tb_List = self.dbObj.readTb()
            tb = tb_List[self.tb_Id][1]
            db_List = self.dbObj.readAll(tb)
            topic = db_List[0][4]
            if (topic is not None):
                self.conButton.config(text=topic)
                self.conButton.place(x=10, y=150)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

        finally:
            self.sideBtn_Load2(db_List)


    def sideBtn_Load2(self, db_List):
        try:
            topic = db_List[1][4]
            if (topic is not None):
                self.conButton1.config(text=topic)
                self.conButton1.place(x=10, y=200)

        except:
            pass

        finally:
            self.sideBtn_Load3(db_List)

    
    def sideBtn_Load3(self, db_List):
        try:
            topic = db_List[2][4]
            if (topic is not None):
                self.conButton2.config(text=topic)
                self.conButton2.place(x=10, y=250)

        except:
            pass

        finally:
            self.sideBtn_Load4(db_List)

    def sideBtn_Load4(self, db_List):
        try:
            topic = db_List[3][4]
            if (topic is not None):
                self.conButton3.config(text=topic)
                self.conButton3.place(x=10, y=300)

        except:
            pass

        finally:
            self.sideBtn_Load5(db_List)

    def sideBtn_Load5(self, db_List):
        try:
            topic = db_List[4][4]
            if (topic is not None):
                self.conButton4.config(text=topic)
                self.conButton4.place(x=10, y=325)

        except:
            pass

        finally:
            self.sideBtn_Load6(db_List)

    def sideBtn_Load6(self, db_List):
        try:
            topic = db_List[5][4]
            if (topic is not None):
                self.conButton5.config(text=topic)
                self.conButton5.place(x=10, y=400)

        except:
            pass

        finally:
            self.sideBtn_Load7(db_List)

    def sideBtn_Load7(self, db_List):
        try:
            topic = db_List[6][4]
            if (topic is not None):
                self.conButton6.config(text=topic)
                self.conButton6.place(x=10, y=450)

        except:
            pass

        finally:
            self.sideBtn_Load8(db_List)

    def sideBtn_Load8(self, db_List):
        try:
            topic = db_List[7][4]
            if (topic is not None):
                self.conButton7.config(text=topic)
                self.conButton7.place(x=10, y=500)

        except:
            pass

        finally:
            self.sideBtn_Load9(db_List)

    def sideBtn_Load9(self, db_List):
        try:
            topic = db_List[8][4]
            if (topic is not None):
                self.conButton8.config(text=topic)
                self.conButton8.place(x=10, y=550)

        except:
            pass

        finally:
            self.sideBtn_Load10(db_List)

    def sideBtn_Load10(self, db_List):
        try:
            topic = db_List[9][4]
            if (topic is not None):
                self.conButton9.config(text=topic)
                self.conButton9.place(x=10, y=600)

        except:
            pass
    
    #######################
    #This section is the method for the all the side button inside the sideTab.
    #When the button is clicked it assigns the current index the certain button. Like button 1 would bring you to dialogue 1.
    #######################
    def conSwitch(self):
        self.currentIndex = 0
        self.load(self.currentIndex)

    def conSwitch1(self):
        self.currentIndex = 1
        self.load(self.currentIndex)
    
    def conSwitch2(self):
        self.currentIndex = 2
        self.load(self.currentIndex)

    def conSwitch3(self):
        self.currentIndex = 3
        self.load(self.currentIndex)

    def conSwitch4(self):
        self.currentIndex = 4
        self.load(self.currentIndex)

    def conSwitch5(self):
        self.currentIndex = 5
        self.load(self.currentIndex)

    def conSwitch6(self):
        self.currentIndex = 6
        self.load(self.currentIndex)

    def conSwitch7(self):
        self.currentIndex = 7
        self.load(self.currentIndex)

    def conSwitch8(self):
        self.currentIndex = 8
        self.load(self.currentIndex)

    def conSwitch9(self):
        self.currentIndex = 9
        self.load(self.currentIndex)

    #####################
    #This section I am creating a simple window with simple buttons and frames and canvas.
    #This is a child window of the main Window.
    #####################
    def editWin(self):
        
        #Making the window.
        self.sideWin = tk.Toplevel(self.mainWin, bg="white")
        self.sideWin.geometry("600x600")
        self.sideWin.resizable(False, False)
        self.sideWin.title("AI imageVariant")

        icon_image = tk.PhotoImage(file="aiAvatar.png")
        self.sideWin.iconphoto(True, icon_image)

        #Setting and making some variables.
        self.filepath = ""
        self.variant_image = ""
        self.side_updateToggle = False


        #Making all the buttons and frames as well as the canvas used.
        self.editorTitle = tk.Label(self.sideWin, text="Image Variation Generator", fg="black", bg="white", font=(5,17))
        self.editorTitle.place(x=45,y=50)

        self.imgCanvas = tk.Canvas(self.sideWin, width=300, height=350, bg="lightgrey")
        self.imgCanvas.place(x=30,y=100)

        self.rightFrame = tk.Frame(self.sideWin, relief=FLAT, width=350, height=600, bg="lightgreen", borderwidth=1)
        self.rightFrame.place(x=350,y=0)

        self.sidebottomframe = tk.Frame(self.sideWin, relief="solid", borderwidth=1, bg="grey")
        self.sidebottomframe.pack(side=tk.BOTTOM, fill=tk.BOTH)

        self.maxBackbutton_SIDE = tk.Button(self.sidebottomframe, text="|<",width=4, height=2, command=self.backConMax_side)

        self.skipBackbutton_SIDE = tk.Button(self.sidebottomframe, text="<<",width=4, height=2, command=self.backCon3_side)

        self.backButton_SIDE = tk.Button(self.sidebottomframe, text="<",width=4, height=2, command=self.backCon_side)

        self.forwardButton_SIDE = tk.Button(self.sidebottomframe, text=">",width=4, height=2, command=self.nextCon_side)

        self.skipForwardButton_SIDE = tk.Button(self.sidebottomframe, text=">>",width=4, height=2, command=self.nextCon3_side)

        self.maxForwardButton_SIDE = tk.Button(self.sidebottomframe, text=">|",width=4, height=2, command=self.nextMax_side)

        self.updateLabel_SIDE = tk.Button(self.sidebottomframe, text=">", width=5, height=2, command=self.side_Update)

        self.deleteButton_SIDE = tk.Button(self.sidebottomframe, text="Delete",width=5, height=2, command=self.side_Delete)
        
        #Packing all the buttons.
        self.maxBackbutton_SIDE.pack(side=tk.LEFT, padx=10, pady=10)
        self.skipBackbutton_SIDE.pack(side=tk.LEFT, padx=10, pady=10)
        self.backButton_SIDE.pack(side=tk.LEFT, padx=10, pady=10)
        self.forwardButton_SIDE.pack(side=tk.LEFT, padx=10, pady=10)
        self.skipForwardButton_SIDE.pack(side=tk.LEFT, padx=10, pady=10)
        self.maxForwardButton_SIDE.pack(side=tk.LEFT, padx=10, pady=10)

        self.blankSIDE = tk.Label(self.sidebottomframe, bg="grey").pack(side=tk.LEFT, padx=20, pady=10)

        self.updateLabel_SIDE.pack(side=tk.RIGHT, padx=10, pady=10)
        self.deleteButton_SIDE.pack(side=tk.RIGHT, padx=10, pady=10)

        self.uploadIMG = tk.Button(self.sideWin, text="Upload Image", command=self.upload_image, bg="lightgreen", width=15, height=2)
        self.uploadIMG.place(x=65,y=470)

        self.saveIMG = tk.Button(self.sideWin, text="Save Image", command=self.save_image, bg="lightgreen", width=15, height=2)
        self.saveIMG.place(x=185,y=470)

        self.submitEdit = tk.Button(self.rightFrame, text="Submit", width=31, bg="white", command=self.editSubmit_Method, fg="black")
        self.submitEdit.place(x=10, y=500)

        #Making a loading bar for the child window.
        self.frame_load = tk.Frame(self.sideWin, relief="solid", borderwidth=1)
        self.frame_load.place(x=100,y=250)
        
        self.progress2 = ttk.Progressbar(self.frame_load, mode='determinate', length=400)
        self.progress2.pack(pady=20, padx=20)

        self.loading_label2 = tk.Label(self.frame_load, text="Loading...", font=("Arial", 12))
        self.loading_label2.pack(pady=5)

        #Hiding it the loading bar.
        self.stopLoad2()

        self.variantIndex = 0

        #Calls load after the init is created.
        self.sideWin.after(100, self.sideWin_Load)

        self.sideWin.mainloop()

    #Upload imag emethod. ALlowing you to upload an image of your chose from your file.
    def upload_image(self):
        try:

            #Use filedialog to open your fle and get the filepath.
            self.filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
            if (self.filepath):

                #Opens the image.
                original_image = Image.open(self.filepath)

                #Get the side of the image canvas.
                canvas_width = self.imgCanvas.winfo_width()
                canvas_height = self.imgCanvas.winfo_height()

                #Set the image size to the canvas.
                resized_image = original_image.resize((canvas_width, canvas_height), resample=Image.LANCZOS)

                #Making it a useable tk object.
                self.background_image = ImageTk.PhotoImage(resized_image)

                #Clearing the img canvas.
                self.imgCanvas.delete("all")

                #Finally inserting it into the canvas.
                self.imgCanvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #THe submit/insert method.
    def editSubmit_Method(self):
        try:
            #FInds the max id to the index to.
            list = self.dbObj.readVariant()
            maxId = len(list)
            self.variantIndex  = maxId

            #Seperate the actual/secoind part of the submit method into a thread to not lag all the other method.
            variantThread = threading.Thread(target=self.editThread)
            variantThread.start()

            #Start the loading bar.
            self.startLoad2()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #thE ACtual submit, insert method.
    def editThread(self):
        try:

            #Use open AI to generate a variantion of a given image.
            client = OpenAI(api_key="<CENSORED_API_KEY>")

            with open(self.filepath, "rb") as image_file:
                response = client.images.create_variation(
                    model="dall-e-2",
                    image=image_file,
                    n=1,
                    size="1024x1024"
                )

            url = response.data[0].url

            #Make a HTTP GET request from the url/
            response = requests.get(url)

            #Get the canvas size.
            canvas_width = self.imgCanvas.winfo_width()
            canvas_height = self.imgCanvas.winfo_height()

            #Get the content of the link and then resizing the image.
            image_data = response.content
            image = Image.open(BytesIO(image_data)).resize((canvas_width, canvas_height), resample=Image.LANCZOS)

            self.variant_image = image

            #Make it a useable image object for tk.
            self.background_image = ImageTk.PhotoImage(image)

            #Inserting it into the image canvas.
            self.imgCanvas.delete("all")
            self.imgCanvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

            #Calling the db class to insert the image as a blob into te database.
            self.dbObj.insert_ImgVariant(image_data)

            #Stop the loading animation.
            self.stopLoad2()
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #Save image method.
    def save_image(self):
        try:

            #Uses the filedialog libary to ask the user if they want to save the image to theri files.
            filepath = filedialog.asksaveasfile(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if (filepath):

                #If they click save then returns filepath. And save the image.
                self.variant_image.save(filepath.name)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    ########################
    #Creating the progress and then starting or stopping the loading bar based off the method.
    #The same as the progress bar method from above.
    ########################
    def startLoad2(self):
        try:
            self.frame_load.place(x=100,y=250)

            self.progress2.start(20)
            self.animateLoad()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))


    def animateLoad2(self):
        try:
            self.loading_label2.config(text=self.loading_label2.cget("text") + ".") 
            if (len(self.loading_label2.cget("text")) > 12):
                self.loading_label2.config(text="Loading")
            self.mainWin.after(500, self.animateLoad2)
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))
    

    def stopLoad2(self):
        try:
            self.progress2.stop()
            time.sleep(0.5)
            self.frame_load.place_forget()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The load method for the child window.
    def sideWin_Load(self):
        try:

            #Pulls the binary data from the blob inside the db table.
            dbList = self.dbObj.readVariant()
            img_data = dbList[self.variantIndex][1]

            #Reading and opening the binary data.
            image = Image.open(BytesIO(img_data))
            
            #Resizing the image.
            canvas_width = self.imgCanvas.winfo_width()
            canvas_height = self.imgCanvas.winfo_height()
            image = image.resize((canvas_width, canvas_height), resample=Image.LANCZOS)

            #Making it into a useable image object for tk.
            self.background_image = ImageTk.PhotoImage(image)

            #Inserting it into the image canvas.
            self.imgCanvas.delete("all")
            self.imgCanvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    ########################
    #This section is the method for the next and back buttons for the side window.
    #It exactly the same as the one for the main window.
    ########################

    #THis method adds 1 to index.
    def nextCon_side(self):
        try:
            dbList = self.dbObj.readVariant()
            if (self.variantIndex < len(dbList) - 1):
                self.variantIndex +=1
                self.sideWin_Load()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #THis methods add 3 to the index.
    def nextCon3_side(self):
        try:
            dbList = self.dbObj.readVariant()
            if (self.variantIndex + 3 < len(dbList)):
                self.variantIndex += 3
            else:
                self.variantIndex = len(dbList) - 1

            self.sideWin_Load()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}".format(error))

    #This method set the index to the max id.
    def nextMax_side(self):
        try:
            dbList = self.dbObj.readVariant()

            max_id = len(dbList) - 1

            self.variantIndex = max_id

            self.sideWin_Load()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}".format(error))

    #This method minus one from the index.
    def backCon_side(self):
        try:
            if (self.variantIndex > 0):
                self.variantIndex -=1
                self.sideWin_Load()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #This method subtracts 3 from the index.
    def backCon3_side(self):
        try:
            if (self.variantIndex - 3 >= 0):
                self.variantIndex -= 3
            else:
                self.variantIndex = 0

            self.sideWin_Load()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}".format(error))

    #Set the index to 0.
    def backConMax_side(self):
        try:
            self.variantIndex = 0
            self.sideWin_Load()
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #The update method. This is a two part method. The first update is just a toggle between commit and the actual update.
    def side_Update(self):
        if (self.side_updateToggle):

            #Starting the update thread.
            variantThread = threading.Thread(target=self.editThread_update)
            variantThread.start()

            #Start the loading bar.
            self.startLoad2()
            self.side_updateToggle = False
        else:
            self.updateLabel_SIDE.config(text="Commit")
            self.side_updateToggle = True

    #Update thread.
    def editThread_update(self):
        try:

            #Using open ai to generate a image variant of the og image.
            client = OpenAI(api_key="<CENSORED_API_KEY>")

            with open(self.filepath, "rb") as image_file:
                response = client.images.create_variation(
                    model="dall-e-2",
                    image=image_file,
                    n=1,
                    size="1024x1024"
                )

            url = response.data[0].url

            #This section is just resizing and make the image a useable tk object.
            response = requests.get(url)

            canvas_width = self.imgCanvas.winfo_width()
            canvas_height = self.imgCanvas.winfo_height()

            image_data = response.content
            image = Image.open(BytesIO(image_data)).resize((canvas_width, canvas_height), resample=Image.LANCZOS)

            self.variant_image = image

            self.background_image = ImageTk.PhotoImage(image)

            #Inserting the image into the canvas.
            self.imgCanvas.delete("all")
            self.imgCanvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

            #FInd the current id the user is on.
            variant_List = self.dbObj.readVariant()
            id = variant_List[self.variantIndex][0]

            #Callign the update method from the db class.
            self.dbObj.updateVariant(image_data, id)

            #Stop load.
            self.stopLoad2()
        
        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #THe delete method toggle method.
    def side_Delete(self):
        try:

            #Ask the user if they want to delete the image.
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete this dialouge where id = {}?" .format(self.variantIndex))

            if (confirm):
                self.confirmDelete_side()

        except Exception as error:
            self.statusLabel.config(text="Status: (ERROR) {}" .format(error))

    #THe actual delete method.
    def confirmDelete_side(self):

        #Finding the id.
        variant_List = self.dbObj.readVariant()
        id = variant_List[self.variantIndex][0]

        #Calling the db class to access the delete method.
        self.dbObj.deleteVariant(id)

        if (self.variantIndex > 0):
            self.variantIndex - 1
            self.sideWin_Load()
        if (self.variantIndex == 0):
            self.variantIndex + 1
            self.sideWin_Load()

    #Declaring a static method.
    @staticmethod

    #This method summarize given text to one sentence.
    def summarizeTx(text, num_sentences=1):
        sentences = sent_tokenize(text)
        
        words = word_tokenize(text.lower())
        
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word.isalnum() and word not in stop_words]
        
        freq_dist = FreqDist(words)
        
        sentence_scores = {}
        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if (word in freq_dist):
                    if (sentence not in sentence_scores):
                        sentence_scores[sentence] = freq_dist[word]
                    else:
                        sentence_scores[sentence] += freq_dist[word]
        
        top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        
        summary = ' '.join(top_sentences)
        
        return summary
    
    #Everytime the scrollCanvas is configure. THis method is called due to a key bind.
    def update_scroll_region(self, event):

        #Configures the canvas.
        self.scrollCanvas.configure(scrollregion=self.scrollCanvas.bbox("all"))