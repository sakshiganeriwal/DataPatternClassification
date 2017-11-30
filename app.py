import numpy as np
import scipy.cluster.hierarchy
import matplotlib.pyplot as plt
import collections
from jellyfish import jaro_distance
import json
import operator
import sys
import time
import re
import math
import random
from threading import Thread
from flask import Flask, render_template, session, request, json
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

thread = Thread()

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

d = dict.fromkeys(['country','age','balance','type','duration'])
colors = []
DicFin = []
Dic = []
Y = []
attributes = []
filterValue = []
prev_t1 = []
prev_t = []
X = []
count = 0
value = []
flag =0
flag1 = 0
operator_dict = {'>' : operator.gt,
                 '>=' : operator.ge,
                 '==' : operator.eq,
                 '<' : operator.lt,
                 '<=' : operator.le}
conditions = ["==",">","<",">=","<="]
t = ["India","canada","pakistan","nigeria","hong kong","china","japan","australia"]
trans_type = ["withdraw","deposit","enquire"]
inp = 0

def gennerate_obj():
    global d
    d = {'country':random.choice(t),
        'age':random.randrange(20,80),
        'balance':random.uniform(1,100000),
        'type':random.choice(trans_type),
        'duration':random.uniform(1,30)
        }
    # print "object generated"
    # print d
    return d    

def lookup(dic, key):
    keys = dic.keys()
    if key in keys:
        value.append(dic.get(key))
    else:
        for each in keys:
            flag = each.find(key)
            if flag >= 0:
                value.append(dic.get(each))
    return

def parse_dict(init, lkey = ''):
    ret = {}
    if isinstance(init,basestring):
        ret[lkey]= str(init)
    else:
        for rkey,val in init.items():
            key = lkey+rkey
            if isinstance(val, dict):
                ret.update(parse_dict(val, key + '_'))
            elif isinstance(val,list):
                for n in val:
                    ret.update(parse_dict(n, key + '_'))
            else:
                ret[str(key)] = str(val)
    return dict(ret)


def java_string_hashcode(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def dist(x,y):
    return np.sqrt(np.sum((x-y)**2))

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

def Select(attributes,filterValue):
    global DicFin
    global value
    global prev_t
    global prev_t1
    global X
    global Y
    X = []
    DicFin = []
    for i1 in range(len(attributes)):
        Y = []
        value = []
        print "attributes type"
        print type(attributes[0])
        for each in Dic:
            lookup(each,attributes[i1])
        print "value"
        print value
        # DicFin.extend(list(set(value)))
        # DicFin = list(set(DicFin))
        # DicFin = value
        # print DicFin
        n = len(value)
        if type(value[0]) is str:
            for i in range(n):
                for j in range(n):
                    if j>i:
                        Y.append(levenshtein(value[i],value[j]))

        else:
            for i in range(n):
                for j in range(n):
                    if j>i:
                        Y.append(dist(value[i],value[j]))          
        if not len(X):
            X = np.zeros(len(Y))
        X = X + Y
    X = X/len(attributes)    
    linkage_matrix = scipy.cluster.hierarchy.linkage(X, "single")
    t=scipy.cluster.hierarchy.fcluster(linkage_matrix,0)
    print "t"
    print t
    del value[:]
    X=[]
    all_keys = set().union(*(d.keys() for d in Dic))
    all_keys = list(all_keys)
    for k in all_keys:
        Y = []
        value = []
        for each in Dic:
            lookup(each,k)
        n=len(value)
        if type(value[0]) is str:
            for i in range(n):
                    for j in range(n):
                        if j>i:
                            Y.append(levenshtein(value[i],value[j]))

        else:
            for i in range(n):
                    for j in range(n):
                        if j>i:
                            Y.append(dist(value[i],value[j]))          
        if not len(X):
            X=np.zeros(len(Y))
        X = X + Y
    X = X/len(all_keys)
    linkage_matrix = scipy.cluster.hierarchy.linkage(X, "single")
    t1=scipy.cluster.hierarchy.fcluster(linkage_matrix,0)
    print "t1"
    print t1
    del value[:]
    print "prev_t"
    print prev_t
    print len(prev_t)
    print "prev_t1"
    print prev_t1
    print len(prev_t1)
    for i in range(len(prev_t)):
        if t[i] != prev_t[i]:
            print prev_t[i]
            c = t[i]
            for idx, item in enumerate(t):
                if item == c:
                    t[idx] = prev_t[i]
                if item == prev_t[i] and idx > i:
                    t[idx] = c
    for i in range(len(prev_t1)):
        if t1[i] != prev_t1[i]:
            print prev_t1[i]
            c = t1[i]
            for idx, item in enumerate(t1):
                if item == c:
                    t1[idx] = prev_t1[i]
                if item == prev_t1[i] and idx > i:
                    t1[idx] = c
    l_t = len(prev_t)
    l_t1 = len(prev_t1)
    prev_t = t
    prev_t1 = t1
    count1=-1
    print "check for operator_func"
    for i1 in range(len(attributes)):
        if len(filterValue[i1]):
            for each in Dic:
                lookup(each,attributes[i1])
            print "attributes[i1]"
            print attributes[i1]
            print "filterValue[i1]"
            print filterValue[i1]
            for c in conditions:
                if c is filterValue[i1]:
                    filterValue[i1] = filterValue[i1].replace(c,"")
                    break
            print "filterValue[i1] after replace"
            if type(value[0]) is str:
                print "its country"
                for i2 in range(len(value)):
                    print "value[i2] in filterValue[i1]"
                    print value[i2]
                    if value[i2] in filterValue[i1]:
                        print "value in operator_func"
                        print value[i2]
                        t1[i2] = count1
                        print "initial t1"
                        print t1
                        print "t1[i2]"
                        print t1

            else:
                operator_func = operator_dict[c]
                print "operator_func"
                print operator_func
                for i2 in range(len(value)):
                    if operator_func(value[i2], filterValue[i1]):
                        print "value in operator_func"
                        print value[i2]
                        t1[i2] = count1
                        print "initial t1"
                        print t1
                        print "t1[i2]"
                        print t1
        count1 = count1-1
    print "t"
    print t
    print len(t)
    print "t1"
    print t1
    print len(t1)
    print "l_t"
    print l_t
    print "l_t1"
    print l_t1
    if not flag1:
        data = {'t': [],'t1': []}
        data['t'].extend(t[l_t:])
        data['t1'].extend(t1[l_t1:])
    else:
        # print "DicFin before"
        # print DicFin
        # DicFin.extend(list(set(value1)))
        # print DicFin
        # DicFin= list(set(DicFin))
        # counter=collections.Counter(t[l_t:])
        # data={'countcluster':[],'uniquecluster':[],'name':[]}
        # data['countcluster'].extend(counter.values())
        # data['uniquecluster'].extend(counter.keys())
        data = {'t': [],'name': []}
        data['t'].extend(t[l_t:])
        data['name'].extend(value[l_t:])
    return data

class MyThread(Thread):
    global attributes
    global filterValue
    def run(self):
        while True:
            time.sleep(2.5)
            for i in range(1,random.randint(4,10)):
                Dic.append(gennerate_obj())
            print "Dic"
            print Dic
            f=Select(attributes,filterValue)
            print "f"
            print f
            fsend=json.dumps(f, cls=MyEncoder)
            socketio.emit('my response', fsend)
            print "Emit sucess"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Scatter.html')
def Scatter():
    return render_template('Scatter.html')

@app.route('/Block.html')
def Block():
    return render_template('Block.html')

@socketio.on('connect')
def test_connect():
    attributes=d.keys()
    attr=json.dumps(attributes,cls=MyEncoder)
    emit('conn', attr)
    
@socketio.on('Blockgenerate')
def test1(dict1):
    global attributes
    global filterValue
    print "in generate"
    print "dict1"
    print dict1
    dict1 = dict1.replace("{","")
    dict1 = dict1.replace("}","")
    dict1 = dict1.replace('"','')
    dict1 = dict1.replace('"','')
    dict1 = dict1.split(',')
    for each in dict1:
        y =each.split(':')
        attributes.append(str(y[0]))
        filterValue.append(str(y[1]))
    print "attributes"
    print attributes
    print "filterValue"
    print filterValue
    MyThread().start()

@socketio.on('Scattergenerate')
def test2(dict1):
    global flag1
    global attributes
    global filterValue
    print "in generate"
    print "dict1"
    print dict1
    dict1 = dict1.replace("{","")
    dict1 = dict1.replace("}","")
    dict1 = dict1.replace('"','')
    dict1 = dict1.replace('"','')
    dict1 = dict1.split(',')
    for each in dict1:
        y =each.split(':')
        attributes.append(str(y[0]))
        filterValue.append(str(y[1]))
    print "attributes"
    print attributes
    print "filterValue"
    print filterValue
    flag1 =1
    MyThread().start()

if __name__ == '__main__':
    socketio.run(app, debug=True,port=7222, host='0.0.0.0')