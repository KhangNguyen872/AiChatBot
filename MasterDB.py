"""
Khang Nguyen
March 18 2024
MasterDB
IST
"""

#Importing mysql connector and dt.
import mysql.connector
import datetime as dt

class dbConnector:

    #Connecting the to the database.
    def connection(self):
        self.connect = mysql.connector.connect(
            host="<CENSORED_HOST>",
            user="<CENSORED_USER>",
            password="<CENSORED_PASSWORD>",     
            database="<CENSORED_DATABASE>"
        )
        
        #Creating a cursor.
        self.cursor = self.connect.cursor()
    
    #Disconnection method.
    def disconnect(self):
        self.connect.disconnect()

    #THis method read everything inside a certain table.
    def readAll(self, tb):
        self.cursor.execute("SELECT * FROM {}" .format(tb))
        return self.cursor.fetchall()
    
    #This method read everything inside the imageVariant table.
    def readVariant(self):
        self.cursor.execute("SELECT * FROM imageVariant")
        return self.cursor.fetchall()
    
    #This method grabs everything from the table dictionaries.
    def readTb(self):
        self.cursor.execute("SELECT * FROM tableDictionaries")
        return self.cursor.fetchall()
    
    #Insert method for the main tables..
    def createDialouge(self, user, ai, date, topic, duration, current_tb):

        #Making sure the ai responds is a string.
        ai_string = str(ai)

        #Definning the query and values.
        query = "INSERT INTO {} (user, ai, date, topic, duration) VALUES (%s, %s, %s, %s, %s)".format(current_tb)
        values = (user, ai_string, date.strftime("%Y-%m-%d %H:%M:%S"), topic, duration)

        #Excuting and commiting the action.
        self.cursor.execute(query, values)
        self.connect.commit()

    #Another insert method. THis method takes binary and insert in as a blob.
    def insert_ImgVariant(self,img):

        #Definning query and values.
        query = "INSERT INTO imageVariant (image) VALUES (%s)"
        values = (img,)

        #Excuting and commiting.
        self.cursor.execute(query, values)
        self.connect.commit()

    #Delete from the main tables method.
    def deleteDialouge(self,id, tb):
        try:

            #Definning query and value.
            query = "DELETE FROM {} WHERE user=%s" .format(tb)
            value = (id,)
            
            self.cursor.execute(query, value)
            self.connect.commit()
        except Exception as error:
            print(error)

    def deleteConDB(self, tb):
        try:
            self.cursor.execute("DROP TABLE {}".format(tb))
            self.cursor.execute("DELETE FROM tableDictionaries WHERE tb_name='{}'".format(tb))

            self.connect.commit()
        except Exception as error:
            print(error)

    def deleteVariant(self,id):
        try:
            query = "DELETE FROM imageVariant WHERE Id=%s"
            value = (id,)
            
            self.cursor.execute(query, value)
            self.connect.commit()
        except Exception as error:
            print(error)

    #Insert table names into te table dictionaries to be used later.
    def insertTb_Name(self, tb_name):
        self.cursor.execute("INSERT INTO tableDictionaries (tb_Name) VALUES('{}')" .format(tb_name))
        self.connect.commit()

    #Creates a new table if not already exiting when called.
    def new_Conversation(self, tb_name):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS {} (id int PRIMARY KEY AUTO_INCREMENT, user TEXT, ai TEXT, date VARCHAR(100), topic TEXT, duration INT, img longblob);" .format(tb_name))
        self.connect.commit

    #This method updates the main tables.
    def updateDB(self, user, ai, date, topic, tb, index):
        try:

            #Making sure ai responds is a string.
            ai_str = str(ai)

            #Definning query and values.
            query = ("UPDATE {} SET user=%s, ai=%s, date=%s, topic=%s WHERE id=%s" .format(tb))
            values = (user, ai_str, date.strftime("%Y-%m-%d %H:%M:%S"), topic, index)

            self.cursor.execute(query, values)
            self.connect.commit()

        except Exception as error:
            print(error)

    #This method updates images from the main tables.
    def updateIMG(self, user, date, topic, duration, tb, index, binary):
        try:
            query = ("UPDATE {} SET user=%s, date=%s, topic=%s, duration=%s, img=%s WHERE id=%s" .format(tb))
            values = (user, date.strftime("%Y-%m-%d %H:%M:%S"), topic, duration, binary, index)

            self.cursor.execute(query, values)
            self.connect.commit()

        except Exception as error:
            print(error)

    #Update iamge form the side tables.
    def updateVariant(self, img, id):
        try:

            query = ("UPDATE imageVariant SET image=%s WHERE Id=%s")
            values = (img, id)

            self.cursor.execute(query, values)
            self.connect.commit()

        except Exception as error:
            print(error)

    #Insert images into the main Tables5
    def img_Insert(self,user,date,topic,duration,tb, binary):

        query = ("INSERT INTO {} (user, date, topic, duration, img) VALUES(%s, %s,%s, %s, %s)" .format(tb))
        values = (user,date.strftime("%Y-%m-%d %H:%M:%S"),topic,duration, binary,)

        self.cursor.execute(query,values)
        self.connect.commit()