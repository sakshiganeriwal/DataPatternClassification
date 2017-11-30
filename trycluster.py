import numpy as np
import scipy.cluster.hierarchy
import matplotlib.pyplot as plt
import collections
from jellyfish import jaro_distance
import json

with open("largetest.json") as json_file:
    Dic = json.load(json_file)
value=[]
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
    if isinstance(init,unicode):
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
DicFin=[]
for each in Dic:
    Dic1= parse_dict(each,'')
    DicFin.append(Dic1)

colors=[]
inp=input("Enter Cluster category:1.country 2.balance 3.gender")
#inp=1
if inp==1:
    for each in DicFin:
        lookup(each,'eyeColor')
elif inp==2:
    for each in DicFin:
        lookup(each,'balance')
elif inp==3:
    for each in DicFin:
        lookup(each,'gender')
else:
    print "choose correct option"
#print "value"
#print value
for each in value:
    num =java_string_hashcode(each)
    colors.append(num)
#print"colors"
#print colors
n=len(value)
#print "n"
#print n
X = []
for i in range(n):
    for j in range(n):
        if j>i:
            X.append(levenshtein(value[i],value[j]))
#print X
linkage_matrix = scipy.cluster.hierarchy.linkage(X, "single")
#print linkage_matrix
fancy_dendrogram(linkage_matrix,p=12,leaf_rotation=90.,leaf_font_size=12.,annotate_above=10)
t=scipy.cluster.hierarchy.fcluster(linkage_matrix,1)
#print t
n1=len(set(t))
#print n1
#print "type of t"
#print type(t)
#sendData = {}
#sendData1 = {}
#for i in range(len(value)):
 #   sendData["name"].add(value[i])
  #  sendData["group"].add(t[i])
   # sendData1.add(sendData)
#FinalData={}
#FinalData["node"]=sendData1
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

m = len(set(t))

d={'m':m,'name':[],'group':[]}
d['name'].extend(value)
d['group'].extend(t)
print d['group']
json_data=json.dumps(d,cls=MyEncoder)
with open("outputfilename.json", 'w') as outfile:
    json.dump(json_data, outfile,cls=MyEncoder)
#print m
#print type(FinalData)
#print FinalData
    #json.dump(value,outfile,cls=MyEncoder)
#plt.show()
