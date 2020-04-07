import math

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
import sys
import os
import zipstream
import pandas as pd
import time
import time

from db import db_helper
from data import data_process
from user import auth
from util import util
from config import validate


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
@login_required
def experiment(request):
    return render(request, 'experiment_py.html')


@login_required
def test_config(request):
    username = request.user.username
    start_tps = 0
    duration = 0
    smart_contract = ""
    failure_type = ""
    start_time = 0
    failure_duration = 0
    level = 1
    xxx_name = ""
    label = ""
    if request.method == "POST":
        start_tps = int(request.POST.get("startTps", None))
        duration = int(request.POST.get("duration", None))
        smart_contract = request.POST.get("smartContract", None)
        failure_type = request.POST.get("type", None)
        start_time = int(request.POST.get("startAfter", None))
        xxx_name = request.POST.get("nodeName", None)
        failure_duration = int(request.POST.get("failure_duration", None))
        level = int(request.POST.get("level", None))
        label = request.POST.get("label", None)
    test_config = util.read_json('static/json/config.json')
    test_config['user'] = username
    test_config['startTps'] = start_tps
    test_config['duration'] = duration
    test_config['smartContract'] = smart_contract
    test_config['status'] = 'pending'
    test_config['startTime'] = int(time.time())
    if not validate.validate_test_config(test_config):
        return render(request, 'testConfig_py.html', {'err_msg': 'Invalid test config.'})
    failure_config = [{
        'type': failure_type,
        'startAfter': start_time,
        'duration': failure_duration,
        'level': level,
        'label': label
    }]
    xxx_name_label = "nodeName"
    if failure_type == "smartContract":
        xxx_name_label = "contractName"
    failure_config[0][xxx_name_label] = xxx_name
    if not validate.validate_failure_config(failure_config):
        return render(request, 'testConfig_py.html', {'err_msg': 'Invalid failure config.'})
    util.write_yaml('static/json/failure.yaml', {'failure': failure_config})
    test_config['failure'] = [failure_config]
    util.write_json('static/json/config.json', test_config)
    db_helper.insert(test_config)
    return render(request, 'testConfig_py.html'
                  , {'msg': 'All config valid.'})


@login_required
def detailed_result(request):
    id = ''
    show_type, next_type = 'smooth', 'raw'
    if request.method == "GET":
        id = request.GET.get("id", None)
        show_type = request.GET.get('type', 'smooth')
    data = db_helper.get_one(id)
    failure, duration, request_rate = data['failure'], data['duration'], data['startTps']
    mean, interval = 7, int(duration / 50)
    if show_type == 'raw':
        mean, interval = math.ceil(duration / 300) * 2 - 1, int(duration / 300)
        next_type = 'smooth'
    data['id'] = id
    data['result']['throughput'] = data_process.proc_data(data['result']['throughput'], mean, interval)
    data['result']['latency'] = data_process.proc_data(data['result']['latency'], mean, interval)
    data['result']['success_rate'] = data_process.success_rate(request_rate, data['result']['throughput'])
    total_mean_throughput = data_process.get_mean_by_period(data['result']['throughput'], 0, -1)
    total_mean_latency = data_process.get_mean_by_period(data['result']['latency'], 0, -1)
    total_mean_success_rate = data_process.get_mean_by_period(data['result']['success_rate'], 0, -1)
    total_median_throughput = data_process.get_median_by_period(data['result']['throughput'], 0, -1)
    total_median_latency = data_process.get_median_by_period(data['result']['latency'], 0, -1)
    total_median_success_rate = data_process.get_median_by_period(data['result']['success_rate'], 0, -1)
    
    failure_metrics = []
    before, after = sys.maxsize, 0
    for f in failure:
        f_s = f['startAfter']
        f_f = f_s + f['duration']
        before = min(before, f_s)
        after = max(after, f_f)
        f_tmp = {
            'label': f['label'],
            'type': f['type'],
            'level': f['level'],
            'start': f_s,
            'finish': f_f
        }
        f_mean_t = data_process.get_mean_by_period(data['result']['throughput'], f_s, f_f)
        f_mean_l = data_process.get_mean_by_period(data['result']['latency'], f_s, f_f)
        f_mean_s = data_process.get_mean_by_period(data['result']['success_rate'], f_s, f_f)
        f_median_t = data_process.get_median_by_period(data['result']['throughput'], f_s, f_f)
        f_median_l = data_process.get_median_by_period(data['result']['latency'], f_s, f_f)
        f_median_s = data_process.get_median_by_period(data['result']['success_rate'], f_s, f_f)
        f_tmp['metrics'] = [f_mean_t, f_mean_l, f_mean_s, f_median_t, f_median_l, f_median_s]
        failure_metrics.append(f_tmp)

    before_mean_throughput = data_process.get_mean_by_period(data['result']['throughput'], 0, before)
    before_mean_latency = data_process.get_mean_by_period(data['result']['latency'], 0, before)
    before_mean_success_rate = data_process.get_mean_by_period(data['result']['success_rate'], 0, before)
    before_median_throughput = data_process.get_median_by_period(data['result']['throughput'], 0, before)
    before_median_latency = data_process.get_median_by_period(data['result']['latency'], 0, before)
    before_median_success_rate = data_process.get_median_by_period(data['result']['success_rate'], 0, before)

    after_mean_throughput = data_process.get_mean_by_period(data['result']['throughput'], after, -1)
    after_mean_latency = data_process.get_mean_by_period(data['result']['latency'], after, -1)
    after_mean_success_rate = data_process.get_mean_by_period(data['result']['success_rate'], after, -1)
    after_median_throughput = data_process.get_median_by_period(data['result']['throughput'], after, -1)
    after_median_latency = data_process.get_median_by_period(data['result']['latency'], after, -1)
    after_median_success_rate = data_process.get_median_by_period(data['result']['success_rate'], after, -1)

    return render(request, 'list_detailedLatency_py.html', {'test': data, 'next_type': next_type, 'before': before,
    'after': after, 'total_metrics': [
        total_mean_throughput, total_mean_latency, total_mean_success_rate,
        total_median_throughput, total_median_latency, total_median_success_rate
    ], 'before_metrics': [
        before_mean_throughput, before_mean_latency, before_mean_success_rate,
        before_median_throughput, before_median_latency, before_median_success_rate
    ], 'after_metrics': [
        after_mean_throughput, after_mean_latency, after_mean_success_rate,
        after_median_throughput, after_median_latency, after_median_success_rate
    ], 'failure_metrics': failure_metrics})


@login_required
def task_list(request):
    username = request.user.username
    now_user = db_helper.get_user(username)
    user_type = now_user['type']
    res = []
    if username == 'admin':
        tmp = db_helper.get_all()
    else:
        tmp = db_helper.get_by_username(username)
    for test in tmp:
        test['id'] = test['_id']
        test['startTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(test['startTime']))
        test['isOwner'] = True
        res.append(test)
    if username != 'admin':
        for sub_user in now_user['subscribedUsers']:
            sub_tmp = db_helper.get_by_username(sub_user)
            for test in sub_tmp:
                test['id'] = test['_id']
                test['startTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(test['startTime']))
                test['isOwner'] = username == 'admin'
                res.append(test)

    return render(request, 'list_py.html', {"user_type": user_type, "all_tests": res})


@login_required
def delete(request):
    id = request.GET.get("id", None)
    db_helper.delete(id)
    return redirect(reverse('task_list'))


@login_required
def deal(request):
    difficulties = []
    gas_limits = []
    difficulty = request.POST.get("Difficulty", None)
    if difficulty != "":
        difficulties.append(difficulty)
    gas_limit = request.POST.get("gaslimit", None)
    if gas_limit != "":
        gas_limits.append(gas_limit)
    client_type = request.POST.get("client_type", None)
    node_count = int(request.POST.get("node_count", None))
    miner_count = int(request.POST.get("miner_count", None))
    if (len(difficulties) != 0):
        data = dict()
        data['difficulty'] = difficulties
        data['gasLimit'] = gas_limits
        data['nodeCount'] = node_count
        data['startUpType'] = 'docker'
        data['clientType'] = client_type
        data['minerCount'] = miner_count
        util.write_json('static/json/config.json', data)
    return render(request, 'testConfig_py.html')


def del_file(path):
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            del_file(path_file)


def load(request):
    utilities = ZipUtilities()
    path_to = "static/download"
    files = os.listdir(path_to)
    if len(files) != 0:
        str = files[0]
        position = str.find('_')
        nameZip = str[0:position]
        for filename in files:
            tmp_dl_path = os.path.join(path_to, filename)
            utilities.toZip(tmp_dl_path, filename)
        # utilities.close()
        response = StreamingHttpResponse(utilities.zip_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(nameZip + ".zip")
        return response
    else:
        tmp_dl_path = "static/temp/Testing.txt"
        utilities.toZip(tmp_dl_path, "Testing.txt")
        response = StreamingHttpResponse(utilities.zip_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("Report is testing.zip")
    return response


def login(request):
    is_valid = auth.user_login(request)
    if is_valid:
        return redirect(reverse('task_list'))
    else:
        return render(request, 'login_py.html', {"err_msg": "Wrong username or password."})


def signup(request):
    if auth.sign_up(request):
        return render(request, 'signup_py.html', {"err_msg": "Sign up success."})
    else:
        return render(request, 'signup_py.html', {"err_msg": "Sign up failed."})


def logout(request):
    auth.logout(request)
    return redirect(reverse('login_view'))


def login_view(request):
    return render(request, 'login_py.html')


def signup_view(request):
    return render(request, 'signup_py.html')


@login_required
def profile(request):
    username = request.user.username
    now_user = db_helper.get_user(username)
    return render(request, 'profile_py.html', {'now_user': now_user})
