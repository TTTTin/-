#coding=utf-8
import random
import time
import requests
import json

from API.celery import app
from OJ.models import Submission, JudgeStatus


@app.task(bind=False, track_started=True)
def judge(submission_id):
    submission = Submission.objects.get(pk=submission_id)
    problem = submission.problem

    url = 'http://10.103.249.2:12358/judge'
    headers = {
        'X-Judge-Server-Token': 'b82fd881d1303ba9794e19b7f4a5e2b79231d065f744e72172ad9ee792909126',
        'content-type': 'application/json',
    }
    if submission.language == 'python3':
        body = {
            'src': submission.code,
            'language_config':
                {
                    "compile": {
                        "src_name": "solution.py",
                        "exe_name": "__pycache__/solution.cpython-35.pyc",
                        "max_cpu_time": 3000,
                        "max_real_time": 5000,
                        "max_memory": 134217728,
                        "compile_command": "/usr/bin/python3 -m py_compile {src_path}",
                    },
                    "run": {
                        "command": "/usr/bin/python3 {exe_path}",
                        "seccomp_rule": "general",
                        "env": ["PYTHONIOENCODING=UTF-8", "LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]
                    },
                },
            'max_cpu_time': problem.time_limit,
            'max_memory': (problem.memory_limit * 1024),
            'test_case_id': submission.problem.pk,
            'output': True
        }
    elif submission.language == 'java':
        body = {
            'src': submission.code,
            'language_config':
                {
                    "name": "java",
                    "compile": {
                        "src_name": "Main.java",
                        "exe_name": "Main",
                        "max_cpu_time": 3000,
                        "max_real_time": 5000,
                        "max_memory": -1,
                        "compile_command": "/usr/bin/javac {src_path} -d {exe_dir} -encoding UTF8"
                    },
                    "run": {
                        "command": "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k -Djava.security.manager -Dfile.encoding=UTF-8 -Djava.security.policy==/etc/java_policy -Djava.awt.headless=true Main",
                        "seccomp_rule": None,
                        "env": ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"],
                        "memory_limit_check_only": 1
                    }

                },
            'max_cpu_time': problem.time_limit,
            'max_memory': (problem.memory_limit * 1024),
            'test_case_id': submission.problem.pk,
            'output': True
        }
    elif submission.language == 'C++':
        body = {
            'src': submission.code,
            'language_config':
                {
                    "compile": {
                        "src_name": "main.cpp",
                        "exe_name": "main",
                        "max_cpu_time": 3000,
                        "max_real_time": 5000,
                        "max_memory": 134217728,
                        "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++11 {src_path} -lm -o {exe_path}",
                    },
                    "run": {
                        "command": "{exe_path}",
                        "seccomp_rule": "c_cpp",
                        "env": ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]
                    }
                },
            'max_cpu_time': problem.time_limit,
            'max_memory': (problem.memory_limit * 1024),
            'test_case_id': submission.problem.pk,
            'output': True
        }
    else:
        #默认python2
        body = {
            'src': submission.code,
            'language_config':
                {
                    "compile": {
                        "src_name": "solution.py",
                        "exe_name": "solution.pyc",
                        "max_cpu_time": 3000,
                        "max_real_time": 5000,
                        "max_memory": 134217728,
                        "compile_command": "/usr/bin/python -m py_compile {src_path}",
                    },
                    "run": {
                        "command": "/usr/bin/python {exe_path}",
                        "seccomp_rule": "general",
                        "env": ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]
                    },
                },
            'max_cpu_time': problem.time_limit,
            'max_memory': (problem.memory_limit * 1024),
            'test_case_id': submission.problem.pk,
            'output': True
        }

    response = requests.post(url, data=json.dumps(body), headers=headers)
    print(response.status_code)
    response = json.loads(response.text)
    print(response['data'])
    problem.submission_number += 1
    #编译成功返回list，编译失败返回string
    if not isinstance(response['data'], list):
        problem.save(update_fields=['submission_number', 'ACrate', ])
        submission.result = JudgeStatus.COMPILE_ERROR
        submission.info = response['data']
        submission.save()
        return
    else:
        max_real_time = 0
        for obj in response['data']:
            if obj['result'] != 0:
                #do not update 'update_time'
                problem.save(update_fields=['submission_number', 'ACrate', ])
                submission.result = obj['result']
                submission.info = obj
                submission.save()
                return
            if max_real_time <= int(obj['real_time']):
                submission.info = obj
        problem.accepted_number += 1
        problem.save(update_fields=['submission_number', 'accepted_number', 'ACrate', ])
        submission.result = JudgeStatus.ACCEPTED
        submission.save()
