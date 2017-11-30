import numpy as np
import scipy.cluster.hierarchy
import matplotlib.pyplot as plt
import collections
from jellyfish import jaro_distance
import json
import time
import math
import random
from threading import Thread
from flask import Flask, render_template, session, request, json
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

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

colors=[]
DicFin=[]
Dic=[]
value=[]
t=["india","canada","pakistan","nigeria","hong kong","china","japan","australia"]
trans_type=["withdraw","deposit","enquire"]
inp=0

def gennerate_obj():
    d={'country':random.choice(t),
        'age':random.randrange(20,80),
        'balance':random.uniform(1,100000),
        'type':random.choice(trans_type),
        'duration':random.uniform(1,30)
        }
    # print "object generated"
    # print d
    return d    

def lookup(dic, key):
    keys=dic.keys()
    if key in keys:
        value.append(dic.get(key))
    else:
        for each in keys:
            flag=each.find(key)
            if flag>=0:
                value.append(dic.get(each))
    return

def parse_dict(init, lkey=''):
    ret = {}
    if isinstance(init,basestring):
        ret[lkey]= str(init)
    else:
        for rkey,val in init.items():
            key = lkey+rkey
            if isinstance(val, dict):
                ret.update(parse_dict(val, key+'_'))
            elif isinstance(val,list):
                for n in val:
                    ret.update(parse_dict(n, key+'_'))
            else:
                ret[str(key)] = str(val)
    return dict(ret)

def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = scipy.cluster.hierarchy.dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('sample index or (cluster size)')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata

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

def dist(x,y):
    return np.sqrt(np.sum((x-y)**2))

def Select(inp):
    global colors
    global DicFin
    global value
    global X
    global clusterlist
    if inp==1:
        for each in Dic:
            lookup(each,'age')
        for each in value:
            if each not in DicFin:
                DicFin.append(each)
            num =java_string_hashcode(each)
            colors.append(num)
        X=findDistance()
    elif inp==2:
        for each in Dic:
            lookup(each,'balance')
        for each in value:
            if each not in DicFin:
                DicFin.append(each)
            num =java_string_hashcode(each)
            colors.append(num)
        X=findDistance()
    elif inp==3:
        for each in Dic:
            lookup(each,'country')
        for each in value:
            if each not in DicFin:
                DicFin.append(each)
            num =java_string_hashcode(each)
            colors.append(num)
        X=findDistance()
    elif inp==4:
        all_keys = set().union(*(d.keys() for d in Dic))
        all_keys=list(all_keys)
        for i in all_keys:
            Y=[]
            for each in Dic:
                lookup(each,i)
            for each in value:
                num =java_string_hashcode(each)
                colors.append(num)
            Y=findDistance()
            if not len(X):
                X=np.zeros(len(Y))
            X = X + Y
        X = X/len(all_keys)
        colors=X
    else:
        print "choose correct option"
    linkage_matrix = scipy.cluster.hierarchy.linkage(X, "single")
    fancy_dendrogram(linkage_matrix,p=12,leaf_rotation=90.,leaf_font_size=12.,annotate_above=10)
    t=scipy.cluster.hierarchy.fcluster(linkage_matrix,1)
    d=[];
    counter=collections.Counter(t)
    d={'numele':len(t),'countcluster':[],'uniquecluster':[],'name':[],'colors':[]}
    d['countcluster'].extend(counter.values())
    d['uniquecluster'].extend(counter.keys())
    d['name'].extend(DicFin)
    d['colors'].extend(colors)
    return d

def findDistance():
    global value
    global X    
    n=len(value)
    X = []
    for i in range(n):
        for j in range(n):
            if j>i:
                X.append(dist(colors[i],colors[j]))
    return X

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    emit('conn', )

@socketio.on('clusterAge')
def test1():
    inp=1
    while True:
        time.sleep(2.5)
        for i in range(1,random.randint(2,10)):
            Dic.append(gennerate_obj())
        print "Dic"
        print Dic
        f=Select(inp)
        print "f"
        print f
        fsend=json.dumps(f,cls=MyEncoder)
        del Dic[:]
        emit('my response', fsend)

        print "Emit sucess"
        
@socketio.on('clusterBalance')
def test2():
    inp = 2
    while True:
        time.sleep(2.5)
        for i in range(1,random.randint(20,30)):
            Dic.append(gennerate_obj())
        f=Select(inp)
        fsend=json.dumps(f,cls=MyEncoder)
        del Dic[:]
        emit('my response', fsend)
        
@socketio.on('clusterCountry')
def test3():
    inp=3
    while True:
        time.sleep(2.5)
        for i in range(1,random.randint(2,10)):
            Dic.append(gennerate_obj())
        f = Select(inp)
        fsend=json.dumps(f,cls=MyEncoder)
        del Dic[:]
        emit('my response', fsend)

@socketio.on('clusterAll')
def test3():
    inp=4
    while True:
        time.sleep(2.5)
        for i in range(1,random.randint(2,10)):
            Dic.append(gennerate_obj())
        f=Select(inp)
        fsend=json.dumps(f,cls=MyEncoder)
        del Dic[:]
        emit('my response', fsend)
        print "Emit sucess"

if __name__ == '__main__':
    socketio.run(app, debug=True,port=7080, host='0.0.0.0')