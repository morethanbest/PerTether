from django.shortcuts import render
from django.shortcuts import  HttpResponse
from django.http import StreamingHttpResponse
import json
import  urllib
from urllib.request import urlretrieve
import shutil
# Create your views here.
import zipfile
import os
import zipstream
import pandas as pd
import time
import threading
class ZipUtilities:
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def toZip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.addFolderToZip(file, name)

    def addFolderToZip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(full_path, arcname=os.path.join(name, os.path.basename(full_path)))
            elif os.path.isdir(full_path):
                self.addFolderToZip(full_path, os.path.join(name, os.path.basename(full_path)))

    def close(self):
        if self.zip_file:
            self.zip_file.close()

# 将请求定位到index.html文件中
def experiment(request):
    return render(request, 'experiment_py.html')

def testConfig(request):
    startTps = 0
    finishTps = 0
    duration=0
    smartcontract = ""
    numArr=[]
    labelArr=[]
    if request.method == "POST":
        startTps = int(request.POST.get("startTps", None))
        finishTps= int(request.POST.get("finishTps", None))
        duration=int(request.POST.get("duration", None))
        smartcontract=request.POST.get("smartcontract", None)
    if (finishTps != 0):
        with open("static/json/config0.json", 'r') as load_f:
            load_dict = json.load(load_f)
        load_dict['startTps']=startTps
        load_dict['finishTps']=finishTps
        load_dict['duration']=duration
        load_dict['smartContract']=smartcontract
        file = open('static/json/config.json', 'w', encoding='utf-8')
        json.dump(load_dict, file, ensure_ascii=False)
        file.close()
        i=1
        start=startTps
        while(start<=finishTps):
            labelArr.append(i)
            numArr.append(start)
            i = i + 1
            start = start * 2
        labelArr[-1]=str(labelArr[-1])+'times'
        # os.chdir('..')
        # result = subprocess.run(['which', 'node'],
        #                         stdout=subprocess.PIPE,
        #                         stderr=subprocess.PIPE)
        # nodeCmd = result.stdout.decode("utf-8").replace('\n', '')
        # pnode = subprocess.Popen(
        #     [nodeCmd, 'src/main.js', '-p', 'gui/static/json/', '-c', 'gui/static/json/config.json'],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE)
        # os.chdir('gui')
    return render(request,'testConfig_py.html',{"labelArr":labelArr,"numArr":numArr})
def throughput(request):
    with open("static/json/config.json", 'r') as load_f:
        load_dict = json.load(load_f)
        m=len(load_dict['gasLimit'])
        n=len(load_dict['difficulty'])
        difficulty = load_dict['difficulty']
        gaslimit = load_dict['gasLimit']
    num=m*n
    exists=[]
    labelAll=[]
    valueAll=[]
    timestampAll=[]
    for i in range(num):
        if os.path.exists("static/json/report"+str(i)+".json"):
            exists.append("T")
            with open("static/json/report"+str(i)+".json", 'r') as load_data:
                info = json.load(load_data)
            throughputArr=info["throughput"]
            labels=[]
            values=[]
            for j in range(len(throughputArr)):
                labels.append(str(throughputArr[j][0])+"tps")
                values.append(round(throughputArr[j][1],2))
            labelAll.append(labels)
            valueAll.append(values)
            timeStamp = info['timestamp']
            timeArray = time.localtime(timeStamp)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            timestampAll.append(otherStyleTime)

        else:
            exists.append("F")
            labels = []
            values = []
            labelAll.append(labels)
            valueAll.append(values)
            timestampAll.append('')
    # print(len(labelAll[1]))
    # print(valueAll)
    return render(request, 'list_throughput_py.html',{"existsArr":exists,"difficulty":difficulty,"gaslimit":gaslimit,"labelAll":labelAll,"valueAll":valueAll,"timestampAll":timestampAll})
def latency(request):
    with open("static/json/config.json", 'r') as load_f:
        load_dict = json.load(load_f)
        m=len(load_dict['gasLimit'])
        n=len(load_dict['difficulty'])
        difficulty = load_dict['difficulty']
        gaslimit = load_dict['gasLimit']
    num=m*n
    exists=[]
    labelAll=[]
    valueAll=[]
    timestampAll = []
    for i in range(num):
        if os.path.exists("static/json/report"+str(i)+".json"):
            exists.append("T")
            with open("static/json/report"+str(i)+".json", 'r') as load_data:
                info = json.load(load_data)
            latencyArr=info["generalLatency"]
            labels=[]
            values=[]
            for j in range(len(latencyArr)):
                labels.append(str(latencyArr[j][0])+"tps")
                values.append(round(latencyArr[j][1],2))
            labelAll.append(labels)
            valueAll.append(values)
            # timestampAll.append(info['timestamp'])
            timeStamp = info['timestamp']
            timeArray = time.localtime(timeStamp)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            timestampAll.append(otherStyleTime)
        else:
            exists.append("F")
            labels = []
            values = []
            labelAll.append(labels)
            valueAll.append(values)
            timestampAll.append('')
    # print(len(labelAll[1]))
    # print(valueAll)
    # print(timestampAll)
    return render(request, 'list_latency_py.html',{"existsArr":exists,"difficulty":difficulty,"gaslimit":gaslimit,"labelAll":labelAll,"valueAll":valueAll,"timestampAll":timestampAll})
def detailedLatency(request):
    with open("static/json/config.json", 'r') as load_f:
        load_dict = json.load(load_f)
        m=len(load_dict['gasLimit'])
        n=len(load_dict['difficulty'])
        difficulty = load_dict['difficulty']
        gaslimit = load_dict['gasLimit']
    num=m*n
    exists=[]
    labelAll=[]
    valueAll=[]
    throughputAll=[]
    maxAll=[]
    timestampAll = []
    for i in range(num):
        if os.path.exists("static/json/report"+str(i)+".json"):
            exists.append("T")
            with open("static/json/report"+str(i)+".json", 'r') as load_data:
                info = json.load(load_data)
            compeltionArr=info["detailedLatency"]
            throughput=[]
            labels = []
            values = []
            maxvalues=[]
            for i in range(len(compeltionArr)):
                throughput.append(compeltionArr[i][0][0])
            for i in range(11):
                if i==10:
                    labels.append(str(compeltionArr[0][i][1])+'gwei')
                else:
                    labels.append(compeltionArr[0][i][1])
            for i in range(len(compeltionArr)):
                v=[]
                for j in range(11):
                    if compeltionArr[i][j][2] is None:
                        compeltionArr[i][j][2]=0
                    v.append(round(compeltionArr[i][j][2],2))
                values.append(v)
                maxvalues.append(max(v))
            labelAll.append(labels)
            valueAll.append(values)
            throughputAll.append(throughput)
            maxAll.append(maxvalues)
            # timestampAll.append(info['timestamp'])
            timeStamp = info['timestamp']
            timeArray = time.localtime(timeStamp)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            timestampAll.append(otherStyleTime)
        else:
            exists.append("F")
            labels = []
            values = []
            throughput=[]
            maxvalues=[]
            labelAll.append(labels)
            valueAll.append(values)
            throughputAll.append(throughput)
            maxAll.append(maxvalues)
            timestampAll.append('')
    return render(request, 'list_detailedLatency_py.html',{"existsArr":exists,"difficulty":difficulty,"gaslimit":gaslimit,"labelAll":labelAll,"valueAll":valueAll,"throughputAll":throughputAll,"maxAll":maxAll,"timestampAll":timestampAll})
def txCompletion(request):
    with open("static/json/config.json", 'r') as load_f:
        load_dict = json.load(load_f)
        m=len(load_dict['gasLimit'])
        n=len(load_dict['difficulty'])
        difficulty = load_dict['difficulty']
        gaslimit = load_dict['gasLimit']
    num=m*n
    exists=[]
    labelAll=[]
    valueAll=[]
    throughputAll=[]
    maxAll=[]
    timestampAll = []
    for i in range(num):
        if os.path.exists("static/json/report"+str(i)+".json"):
            exists.append("T")
            with open("static/json/report"+str(i)+".json", 'r') as load_data:
                info = json.load(load_data)
            compeltionArr=info["txCompeltion"]
            throughput=[]
            labels = []
            values = []
            maxvalues=[]
            for i in range(len(compeltionArr)):
                throughput.append(compeltionArr[i][0][0])
            for i in range(11):
                if i==10:
                    labels.append(str(compeltionArr[0][i][1])+'gwei')
                else:
                    labels.append(compeltionArr[0][i][1])
            for i in range(len(compeltionArr)):
                v=[]
                for j in range(11):
                    if compeltionArr[i][j][2] is None:
                        compeltionArr[i][j][2]=0
                    v.append(round(compeltionArr[i][j][2],2))
                values.append(v)
                maxvalues.append(max(v))
            labelAll.append(labels)
            valueAll.append(values)
            throughputAll.append(throughput)
            maxAll.append(maxvalues)
            # timestampAll.append(info['timestamp'])
            timeStamp = info['timestamp']
            timeArray = time.localtime(timeStamp)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            timestampAll.append(otherStyleTime)
        else:
            exists.append("F")
            labels = []
            values = []
            throughput=[]
            maxvalues=[]
            labelAll.append(labels)
            valueAll.append(values)
            throughputAll.append(throughput)
            maxAll.append(maxvalues)
            timestampAll.append('')
    # print(throughputAll)
    # print(valueAll)
    return render(request, 'list_txCompeltion_py.html',{"existsArr":exists,"difficulty":difficulty,"gaslimit":gaslimit,"labelAll":labelAll,"valueAll":valueAll,"throughputAll":throughputAll,"maxAll":maxAll,"timestampAll":timestampAll})
def deal(request):
    difficulty = [];
    gaslimit = [];
    start_type = "";
    client_type = "";
    nodeCount = 0;
    minerCount=0
    if request.is_ajax():
        difficulty1 = request.POST.get("Difficulty1", None)
        difficulty2 = request.POST.get("Difficulty2", None)
        difficulty3 = request.POST.get("Difficulty3", None)
        if difficulty1 != "":
            difficulty.append(difficulty1)
        if difficulty2 != "":
            difficulty.append(difficulty2)
        if difficulty3 != "":
            difficulty.append(difficulty3)
        gaslimit1 = request.POST.get("gaslimit1", None)
        gaslimit2 = request.POST.get("gaslimit2", None)
        gaslimit3 = request.POST.get("gaslimit3", None)
        if gaslimit1 != "":
            gaslimit.append(gaslimit1)
        if gaslimit2 != "":
            gaslimit.append(gaslimit2)
        if gaslimit3 != "":
            gaslimit.append(gaslimit3)
        start_type = request.POST.get("start_type", None)
        client_type = request.POST.get("client_type", None)
        nodeCount = int(request.POST.get("node_count", None))
        minerCount=int(request.POST.get("miner_count", None))
        if (len(difficulty) != 0):
            data = {}
            data['difficulty'] = difficulty;
            data['gasLimit'] = gaslimit;
            data['nodeCount'] = nodeCount;
            data['startUpType'] = start_type;
            data['clientType'] = client_type;
            data['minerCount']=minerCount
            file = open('static/json/config0.json', 'w', encoding='utf-8')
            json.dump(data, file, ensure_ascii=False)
            file.close()
            ret={"difficulty": difficulty, "gaslimit": gaslimit}
        return HttpResponse(json.dumps(ret))
    else:
        return render(request, 'experiment_py.html' )
def del_file(path):
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            del_file(path_file)
def load(request):
    utilities = ZipUtilities()
    path_to="static/download"
    files=os.listdir(path_to)
    str=files[0]
    position=str.find('_')
    nameZip=str[0:position]
    for filename in files:
        tmp_dl_path = os.path.join(path_to, filename)
        utilities.toZip(tmp_dl_path, filename)
    # utilities.close()
    response = StreamingHttpResponse(utilities.zip_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(nameZip+".zip")
    return response
def download(request):
    del_file('static/download')
    if request.is_ajax():
        urls = request.POST.get("urls", None)
        name=request.POST.get("name", None)
        urls=json.loads(urls)
        for i in range(len(urls)):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;WOW64;rv:64.0) Gecko/20100101 Firefox/64.0'}
            req = urllib.request.Request(url=urls[i], headers=headers)
            data = urllib.request.urlopen(req).read()
            with open("static/download/"+name+"_report"+str(i+1)+".jpg", "wb") as code:
                code.write(data)
            oldname = "static/json/report"+str(i)+".json"
            newname = "static/download/"+name+"_report"+str(i+1)+".json"
            shutil.copyfile(oldname, newname)
            with open("static/json/report"+str(i)+".json", 'r') as load_data:
                info = json.load(load_data)
            datainfo=info[name]
            all=datainfo
            if name=="throughput" :
                name_attribute = ['Frequency', 'Throughput']
            if name=="generalLatency":
                name_attribute = ['Frequency', 'Latency']
            if name=="txCompeltion":
                name_attribute = ['Frequency','GasLimit', 'txCompletion']
                all=[]
                for a in range(len(datainfo)):
                    for b in range(11):
                        all.append(datainfo[a][b])
            if name=="detailedLatency":
                name_attribute = ['Frequency','GasLimit', 'detailedLatency']
                all=[]
                for a in range(len(datainfo)):
                    for b in range(11):
                        all.append(datainfo[a][b])
            writerCSV = pd.DataFrame(columns=name_attribute, data=all)
            writerCSV.to_csv('static/download/'+name+'_report'+str(i+1)+'.csv', encoding='utf-8')
        ret={"res":1}
    return  HttpResponse(json.dumps(ret))


