from flask import Flask,render_template,request,url_for,redirect
import requests,json
from bs4 import BeautifulSoup
from googletrans import Translator
import speech_recognition as sr
import os
import winsound
app = Flask(__name__)
app.static_folder = 'static'
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImtzYWl2ZW51MjAxMEBnbWFpbC5jb20iLCJyb2xlIjoiVXNlciIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL3NpZCI6IjQ1NTgiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3ZlcnNpb24iOiIyMDAiLCJodHRwOi8vZXhhbXBsZS5vcmcvY2xhaW1zL2xpbWl0IjoiOTk5OTk5OTk5IiwiaHR0cDovL2V4YW1wbGUub3JnL2NsYWltcy9tZW1iZXJzaGlwIjoiUHJlbWl1bSIsImh0dHA6Ly9leGFtcGxlLm9yZy9jbGFpbXMvbGFuZ3VhZ2UiOiJlbi1nYiIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvZXhwaXJhdGlvbiI6IjIwOTktMTItMzEiLCJodHRwOi8vZXhhbXBsZS5vcmcvY2xhaW1zL21lbWJlcnNoaXBzdGFydCI6IjIwMTktMDEtMzAiLCJpc3MiOiJodHRwczovL3NhbmRib3gtYXV0aHNlcnZpY2UucHJpYWlkLmNoIiwiYXVkIjoiaHR0cHM6Ly9oZWFsdGhzZXJ2aWNlLnByaWFpZC5jaCIsImV4cCI6MTU3OTM2NzA0MiwibmJmIjoxNTc5MzU5ODQyfQ.w3KpYzImY5pegp8mvyLWtlZ2ONFMwGuaFGUni27ICXQ"
@app.route('/',methods = ['POST','GET'])
def predict_disease():
    if request.method == 'GET':
        return render_template('index2.html',content = {'prediction':""})
    elif request.method == 'POST':
        symptoms_list = request.form.getlist('sym')
        gender = request.form['gender']
        y_o_b = request.form['y_o_b']
        symptoms = [int(x) for x in symptoms_list]
        symptoms = json.dumps(symptoms)
        print(symptoms)
        response = requests.get("https://sandbox-healthservice.priaid.ch/diagnosis",{"token": TOKEN,
                    "language":"en-gb",
                    "symptoms":symptoms,
                    "gender":gender,
                    "year_of_birth":int(y_o_b)})
        data = response.json()
        print(str(data))
        prediction = "We suspect you have "+data[0]['Issue']['Name']+"."
        headers = {'token':'e83fdb800e605f9de054e7b9e61b17f1b53b976e','content-type':'application/json'}
        dt = json.dumps({'data':["We suspect you have "+data[0]['Issue']['Name'],"You could try crocin"],'tgt':'hi','src':'en'})
        response_2 = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
        hindi_dt = response_2.json()
        print(str(hindi_dt))
        hindi_p = hindi_dt['data']['result'][0][0]
        print(hindi_p)
        return render_template('index2.html',content = {'prediction':prediction,'hindi':hindi_p})

@app.route('/updates',methods = ['POST','GET'])
def updates():
    if request.method == 'GET':
        r3 = requests.get("https://newsapi.org/v2/top-headlines",{"country":"in",
                                                          "category":"health",
                                                          "apiKey":"4bd2cc45173342d59a8a71375f34edaa"})
        data_r = r3.json()
        articles = list()
        articles.append({'hindititle':"",'title':"अपने क्षेत्र में महामारी",'desc': "Many people have reported swine flu in your area",'url':""})
        headers = {'token':'e83fdb800e605f9de054e7b9e61b17f1b53b976e','content-type':'application/json'}

        for i in range(0,5):
            if i!=0 and i!=1 and i!=3:
                dt = json.dumps({'data':[data_r['articles'][i]['title']],'tgt':'hi','src':'en'})
                response = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
                hindi_dt = response.json()
                print(hindi_dt['data']['result'][0][0])
                dict = {
                    'hindititle' : hindi_dt['data']['result'][0][0],
                    'title' : data_r['articles'][i]['title'],
                    'desc' : data_r['articles'][i]['description'],
                    'url' : data_r['articles'][i]['url']
                }
                articles.append(dict)
        return render_template('updates.html',content = {'articles':articles})

@app.route('/viewpage',methods = ['POST','GET'])
def viewpage():
    if request.method == 'POST':
        print(request.form['link'])
        page = requests.get(request.form['link']).text
        soup = BeautifulSoup(page)
        tags = soup.find_all(['p','h1','h2','h3','h4','h5','h6'])
        headers = {'token':'e83fdb800e605f9de054e7b9e61b17f1b53b976e','content-type':'application/json'}
        html = "<!DOCTYPE html><head><title>Article</title><head><body>"
        flag = 0
        h_title = ""
        for i in tags:
            if i.name == 'p':
                html = html + "<p>"+i.text+"</p>"
            elif i.name == 'h1':
                if flag == 0:
                    dt = json.dumps({'data':[i.text],'tgt':'hi','src':'en'})
                    #dt = {'data':[i.text],'tgt':'hi','src':'en'}
                    response = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
                    hindi_dt = response.json()
                    #html = html + "<form action=/"tts/" method=/"post/"><input type=/"hidden/" name=/"hindititle/" value=/"><input type=/"submit/" value=/"Listen/"></form>"
                    html = html + "<a href="+'"/tts/<'+hindi_dt['data']['result'][0][0]+'>"><h1>'+hindi_dt['data']['result'][0][0]+"</h1></a>"
                    h_title = hindi_dt['data']['result'][0][0]
                    flag = 1
                else:
                    html = html + "<h1>"+i.text+"</h1>"
            elif i.name == 'h2':
                if flag == 0:
                    dt = json.dumps({'data':[i.text],'tgt':'hi','src':'en'})
                    #dt = {'data':[i.text],'tgt':'hi','src':'en'}
                    response = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
                    hindi_dt = response.json()
                    #html = html + "<h2>"+hindi_dt['data']['result'][0][0]+"</h2>"
                    html = html + "<a href="+'"tts/<'+hindi_dt['data']['result'][0][0]+'>"><h2>'+hindi_dt['data']['result'][0][0]+"</h2></a>"
                    h_title = hindi_dt['data']['result'][0][0]
                    flag = 1
                else:
                    html = html + "<h2>"+i.text+"</h2>"
            elif i.name == 'h3':
                if flag == 0:
                    dt = json.dumps({'data':[i.text],'tgt':'hi','src':'en'})
                    #dt = {'data':[i.text],'tgt':'hi','src':'en'}
                    response = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
                    hindi_dt = response.json()
                    #html = html + "<h3>"+hindi_dt['data']['result'][0][0]+"</h3>"
                    html = html + "<a href="+'"tts/<'+hindi_dt['data']['result'][0][0]+'>"><h3>'+hindi_dt['data']['result'][0][0]+"</h3></a>"
                    h_title = hindi_dt['data']['result'][0][0]
                    flag = 1
                else:
                    html = html + "<h3>"+i.text+"</h3>"
            elif i.name == 'h4':
                if flag == 0:
                    dt = json.dumps({'data':[i.text],'tgt':'hi','src':'en'})
                    #dt = {'data':[i.text],'tgt':'hi','src':'en'}
                    response = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
                    hindi_dt = response.json()
                    #html = html + "<h4>"+hindi_dt['data']['result'][0][0]+"</h4>"
                    html = html + "<a href="+'"tts/<'+hindi_dt['data']['result'][0][0]+'>"><h4>'+hindi_dt['data']['result'][0][0]+"</h4></a>"
                    h_title = hindi_dt['data']['result'][0][0]
                    flag = 1
                else:
                    html = html + "<h4>"+i.text+"</h4>"
            elif i.name == 'h5':
                if flag == 0:
                    dt = json.dumps({'data':[i.text],'tgt':'hi','src':'en'})
                    #dt = {'data':[i.text],'tgt':'hi','src':'en'}
                    response = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
                    hindi_dt = response.json()
                    #html = html + "<h5>"+hindi_dt['data']['result'][0][0]+"</h5>"
                    html = html + "<a href="+'"tts/<'+hindi_dt['data']['result'][0][0]+'>"><h5>'+hindi_dt['data']['result'][0][0]+"</h5></a>"
                    h_title = hindi_dt['data']['result'][0][0]
                    flag = 1
                else:
                    html = html + "<h5>"+i.text+"</h5>"
            elif i.name == 'h6':
                if flag == 0:
                    #dt = json.dumps({'data':[i.text],'tgt':'hi','src':'en'})
                    dt = {'data':[i.text],'tgt':'hi','src':'en'}
                    response = requests.request("post","https://hackapi.reverieinc.com/nmt",data=dt,headers=headers)
                    hindi_dt = response.json()
                    #html = html + "<h6>"+hindi_dt['data']['result'][0][0]+"</h6>"
                    html = html + "<a href="+'"tts/<'+hindi_dt['data']['result'][0][0]+'>"><h6>'+hindi_dt['data']['result'][0][0]+"</h6></a>"
                    h_title = hindi_dt['data']['result'][0][0]
                    flag = 1
                else:
                    html = html + "<h6>"+i.text+"</h6>"

        #---------------#
        #headers = {'token':'e83fdb800e605f9de054e7b9e61b17f1b53b976e','content-type':'application/json'}
        data = json.dumps({'text':h_title,'lang':'hi'})
        response = requests.request("post","https://hackapi.reverieinc.com/tts",data=data,headers=headers)
        x=response._content
        while(True):
            try:
                with open('templates/myfile2.wav', mode='bx') as f:
                    f.write(x)
                break
            except:
                os.remove('templates/myfile2.wav')
        #os.system('/templates/myfile2.wav')
        #winsound.PlaySound('myfile2.wav',winsound.SND_ASYNC)
        #----------------#
        html = html + "</body></html>"
        print(html)
        return html
    elif request.method == 'GET':
        return "hello world"
@app.route('/suggest',methods = ['GET','POST'])
def suggest():
    if request.method == 'GET':
        return render_template('page2.html',content = {"text":"Click mic to start speaking"})

@app.route('/speech', methods = ['POST','GET'])
def speech():
    if request.method == 'GET':
        text = ""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio,language = 'hi-IN')
        except:
            text = "Error"
        #headers = {'token':'e83fdb800e605f9de054e7b9e61b17f1b53b976e','content-type':'application/json'}
        #data = json.dumps({'data':[text],'tgt':'en','src':'hi'})
        #text_in_en =  requests.request("post","https://hackapi.reverieinc.com/nmt",data=data,headers=headers)
        #print(str(text_in_en.json()))
        trans = Translator()
        x = trans.translate(text,src="hi")
        url = "https://fapimail.p.rapidapi.com/email/send"
        text_to_send = "Patient : sathvik\nPhone NUmber : 993296765\nProblem:"+x.text
        payload = json.dumps({ "recipient": "ksaivenu2010@gmail.com",    "sender": "fareed2000ahmed@gmail.com",    "subject": "Expert opinion",    "message": text_to_send})
        headers = {
            'x-rapidapi-host': "fapimail.p.rapidapi.com",
            'x-rapidapi-key': "eb378e65dfmsh2709d2ee1e0b591p193b92jsn1820d2d36ffc",
            'content-type': "application/json",
            'accept': "application/json"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        #reso = requests.post("http://b6c2d9c9.ngrok.io",data = {'text':str(x.text)})
        return render_template("page2.html",content = {"text":text})
@app.route('/tts/<title>',methods=['GET','POST'])
def tts(title):
    headers = {'token':'e83fdb800e605f9de054e7b9e61b17f1b53b976e','content-type':'application/json'}
    data = json.dumps({'text':title,'lang':'hi'})
    response = requests.request("post","https://hackapi.reverieinc.com/tts",data=data,headers=headers)
    x=response._content
    while(True):
        try:
            with open('/templates/myfile2.wav', mode='bx') as f:
                f.write(x)
            break
        except:
            os.remove('myfile2.wav')
    os.system('myfile2.wav')
    winsound.PlaySound('myfile2.wav',winsound.SND_ASYNC)

    return ""

if __name__ == "__main__":
    app.run(debug=True)
