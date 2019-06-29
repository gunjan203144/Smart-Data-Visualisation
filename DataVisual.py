import matplotlib.pyplot as plt
import collections
import pandas as pd
import numpy as np
res=[]

"""
meta=[
 {"colIndex":0,"colName":"month","colType":"Varchar"},
 {"colIndex":1,"colName":"AHT","colType":"Float","unit":"Seconds","type":"aC"}
]

dic={}
for d in meta:
    for key in d.keys():
        if(key=='colType'):
            if(d['colType']=='Varchar'):
                strL.append(d['colIndex'])
            elif(d['colType']=='Integer' or d['colType']=='Float'):
                intL.append(d['colIndex'])
            elif(d['colType']=='date'):
                dateL.append(d['colIndex'])
        elif(key=='unit'):
            if d['unit'] in dic.keys():
                dic[d['unit']].append(d['colIndex'])
            else:
                li=[d['colIndex']]
                dic[d['unit']]=li
"""    
class DrawShapes:
    def line(col1, labelx, col2, labely):
        X= col1.reshape(-1,1)
        y = col2.reshape(-1,1)
        plt.scatter(X, y, color = 'red')
        plt.plot(X, y, color = 'black')
        plt.xlabel(labelx)
        plt.ylabel(labely)
        plt.show()
    
    def groupedBar(col1, str1, col2, str2, labelx, labely):
        ind = np.arange(len(col1))
        width = 0.35
        fig, ax = plt.subplots()
        rects1 = ax.bar(ind - width/2, col1, width,  label=str1)
        rects2 = ax.bar(ind + width/2, col2, width,  label=str2)
        ax.set_ylabel(labely)
        ax.set_xticks(ind)
        ax.legend()
        def autolabel(rects, xpos='center'):
            ha = {'center': 'center', 'right': 'left', 'left': 'right'}
            offset = {'center': 0, 'right': 1, 'left': -1}        
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height), xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(offset[xpos]*3, 3), textcoords="offset points",  ha=ha[xpos], va='bottom')
        autolabel(rects1, "left")
        autolabel(rects2, "right")
        fig.tight_layout()
        plt.show()

    def scatter(col1, labelx,  col2, labely):
        plt.scatter(col1, col2, s = 10, c = 'red', label = 'Clusters')
        plt.xlabel(labelx)
        plt.ylabel(labely)
        plt.show()
        
    def bar(label, labelx, progress, labely):
        index = np.arange(len(label))
        plt.bar(index, progress, color='red')
        plt.xticks(index, label, fontsize=10, rotation=30)
        plt.xlabel(labelx)
        plt.ylabel(labely)
        plt.show()
    
    def pie(labels, sizes):
        plt.pie(sizes, labels=labels, startangle=90, autopct='%.1f%%')
        plt.axis('equal')
        plt.show()
        
class DecisionTree:
    def dataType(fileName):
        dataset=pd.read_csv(fileName)
        intL=[]
        strL=[]
        dateL=[]
        for i in range(0, dataset.iloc[0,:].size):
            typ=input()
            if(typ=='float' or typ=='int'):
                intL.append(i)
            elif(typ=='date'):
                dateL.append(i)
            else:
                strL.append(i)    
        return intL, dateL, strL
    """
            if(dataset.iloc[:,i].dtype=='int32' or dataset.iloc[:,i].dtype=='float32' or dataset.iloc[:,i].dtype=='float64' or dataset.iloc[:,i].dtype=='int64'):
                intL.append(i)
            elif():
                dateL.append(i)
            else:
                strL.append(i)
        return intL,strL
    """
    def chartType(fileName):
        rem=[]
        dateCat=[]
        strCat=[]
        dictionary={}
        intL, dateL, strL=DecisionTree.dataType(fileName)
        dataset=pd.read_csv(fileName)
        for y in dateL:
            freq=collections.Counter(dataset.iloc[:,y].values)
            if(max(freq.values())>1):
                dateCat.append(y)
                rem.append(y)
        for i in dateCat:
            freq=collections.Counter(dataset.iloc[:,i].values)
            dateDic={}
            for k in freq.keys():
                li=[]
                for rd in range(0, dataset.iloc[:,0].size):
                    if(dataset.iloc[rd,i]==k):
                        li.append(rd)
                dateDic[k]=li
            dictionary[i]=dateDic
        for i in dateCat:
            for j in intL:
                x=[]
                y=[]                    
                for k in dictionary[i].keys():
                    x.append(k)
                    s=0
                    for rd in dictionary[i][k]:
                        s=s+dataset.iloc[rd,j]
                    y.append(s)
                if(len(x)<20):
                    d={}
                    d['type']='bar'
                    data={}
                    data['x-axis']=np.array(x)
                    data['y-axis']=np.array(y)
                    data['label']=[dataset.iloc[:,i].name,dataset.iloc[:,j].name]
                    d['info']=data
                    res.append(d)
                else:
                    d1={}
                    d1['type']='line'
                    data1={}
                    data1['x-axis']=np.array(x)
                    data1['y-axis']=np.array(y)
                    data1['label']=[dataset.iloc[:,i].name,dataset.iloc[:,j].name]
                    d1['info']=data1
                    res.append(d1)
        for x in intL:
            for y in intL:
                if x is not y:
                    for z in dateCat:
                        if(len(dictionary[z])<6):
                            d={}
                            d['type']='groupedLine'
                            data={}
                            data['x-axis']=dataset.iloc[:,x].values
                            data['y-axis']=dataset.iloc[:,y].values
                            data['series']=dataset.iloc[:,z].values
                            data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d['info']=data
                            res.append(d)
                            d1={}
                            d1['type']='groupedScatter'
                            data1={}
                            data1['x-axis']=dataset.iloc[:,x].values
                            data1['y-axis']=dataset.iloc[:,y].values
                            data1['series']=dataset.iloc[:,z].values
                            data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d1['info']=data1
                            res.append(d1)
                        d={}
                        d['type']='groupedBar'
                        data={}
                        data['x-axis']=dataset.iloc[:,z].values
                        data['y-axis']=[dataset.iloc[:,x].values, dataset.iloc[:,y].values]
                        data['series']=[dataset.iloc[:,x].values, dataset.iloc[:,y].values]
                        data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d['info']=data
                        res.append(d)
        if(len(strL)!=0): 
            for y in strL:
                freq=collections.Counter(dataset.iloc[:,y].values)
                if(max(freq.values())>1):
                    strCat.append(y)
                    rem.append(y)
            for i in strCat:
                freq=collections.Counter(dataset.iloc[:,i].values)
                strDic={}
                for k in freq.keys():
                    li=[]
                    for rd in range(0, dataset.iloc[:,0].size):
                        if(dataset.iloc[rd,i]==k):
                            li.append(rd)
                    strDic[k]=li
                dictionary[i]=strDic
            for x in intL:
                for y in intL:
                    if x is not y:
                        for z in strCat:
                            if(len(dictionary[z])<6):
                                d={}
                                d['type']='groupedLine'
                                data={}
                                data['x-axis']=dataset.iloc[:,x].values
                                data['y-axis']=dataset.iloc[:,y].values
                                data['series']=dataset.iloc[:,z].values
                                data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                                d['info']=data
                                res.append(d)
                                d1={}
                                d1['type']='groupedScatter'
                                data1={}
                                data1['x-axis']=dataset.iloc[:,x].values
                                data1['y-axis']=dataset.iloc[:,y].values
                                data1['series']=dataset.iloc[:,z].values
                                data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                                d1['info']=data1
                                res.append(d1)
                            d={}
                            d['type']='groupedBar'
                            data={}
                            data['x-axis']=dataset.iloc[:,z].values
                            data['y-axis']=[dataset.iloc[:,x].values, dataset.iloc[:,y].values]
                            data['series']=[dataset.iloc[:,x].values, dataset.iloc[:,y].values]
                            data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d['info']=data
                            res.append(d)
            for y in intL:
                for x in dateL:
                    for z in strCat:
                        if(len(dictionary[z])<6):
                            d={}
                            d['type']='groupedLine'
                            data={}
                            data['x-axis']=dataset.iloc[:,x].values
                            data['y-axis']=dataset.iloc[:,y].values
                            data['series']=dataset.iloc[:,z].values
                            data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d['info']=data
                            res.append(d)
                            d1={}
                            d1['type']='groupedScatter'
                            data1={}
                            data1['x-axis']=dataset.iloc[:,x].values
                            data1['y-axis']=dataset.iloc[:,y].values
                            data1['series']=dataset.iloc[:,z].values
                            data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d1['info']=data1
                            res.append(d1)
                        d={}
                        d['type']='groupedBar'
                        data={}
                        data['x-axis']=dataset.iloc[:,x].values
                        data['y-axis']=dataset.iloc[:,y].values
                        data['series']=dataset.iloc[:,z].values
                        data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d['info']=data
                        res.append(d)
            for i in strCat:
                for j in intL:
                    x=[]
                    y=[]
                    for k in dictionary[i].keys():
                        x.append(k)
                        s=0
                        for rd in dictionary[i][k]:
                            s=s+dataset.iloc[rd,j]
                        y.append(s)
                    if(len(x)<20):
                        d={}
                        d['type']='bar'
                        data={}
                        data['x-axis']=np.array(x)
                        data['y-axis']=np.array(y)
                        data['label']=[dataset.iloc[:,i].name,dataset.iloc[:,j].name]
                        d['info']=data
                        res.append(d)
                    else:
                        d1={}
                        d1['type']='line'
                        data1={}
                        data1['x-axis']=np.array(x)
                        data1['y-axis']=np.array(y)
                        data1['label']=[dataset.iloc[:,i].name,dataset.iloc[:,j].name]
                        d1['info']=data1
                        res.append(d1)
            if(dataset.iloc[:,0].size<11):   
                for x in strL:
                    if x not in rem:
                        for y in intL:
                            if(int(dataset.iloc[:,y].sum())==100 and min(dataset.iloc[:,y].values)>=0):
                                d={}
                                d['type']='pie'
                                data={}
                                data['x-axis']=dataset.iloc[:,x].values
                                data['y-axis']=dataset.iloc[:,y].values
                                data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                                d['info']=data
                                res.append(d)
                            elif(dataset.iloc[:,0].size<6):
                                if(min(dataset.iloc[:,y].values)>=0):
                                    d1={}
                                    d1['type']='pie'
                                    data1={}
                                    data1['x-axis']=dataset.iloc[:,x].values
                                    data1['y-axis']=dataset.iloc[:,y].values
                                    data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                                    d1['info']=data1
                                    res.append(d1)
                                d2={}
                                d2['type']='bar'
                                data2={}
                                data2['x-axis']=dataset.iloc[:,x].values
                                data2['y-axis']=dataset.iloc[:,y].values
                                data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                                d2['info']=data2
                                res.append(d2)
                            else:
                                d1={}
                                d1['type']='pie'
                                data1={}
                                data1['x-axis']=dataset.iloc[:,x].values
                                data1['y-axis']=dataset.iloc[:,y].values
                                data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                                d1['info']=data1
                                d2={}
                                d2['type']='bar'
                                data2={}
                                data2['x-axis']=dataset.iloc[:,x].values
                                data2['y-axis']=dataset.iloc[:,y].values
                                data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                                d2['info']=data2
                                res.append(d2)
                                if(min(dataset.iloc[:,y].values)>=0):
                                    res.append(d1)
                    
            elif(dataset.iloc[:,0].size<31):
                for x in strL:
                    if x not in rem:
                        for y in intL:
                            d={}
                            d['type']='bar'
                            data={}
                            data['x-axis']=dataset.iloc[:,x].values
                            data['y-axis']=dataset.iloc[:,y].values
                            data['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d['info']=data
                            res.append(d)
            for x in strCat:
                y=[]
                X=[]
                for key in dictionary[x].keys(): 
                    X.append(key)
                    y.append(len(dictionary[x][key]))
                if(len(y)<6):
                    d={}
                    d['type']='pie'
                    data={}
                    data['x-axis']=np.array(X)
                    data['y-axis']=np.array(y)
                    data['label']=[dataset.iloc[:,x].name,'Composition']
                    d['info']=data
                    res.append(d)
                d={}
                d['type']='bar'
                data={}
                data['x-axis']=np.array(X)
                data['y-axis']=np.array(y)
                data['label']=[dataset.iloc[:,x].name,'Composition']
                d['info']=data
                res.append(d)
        for x in dateCat:
            y=[]
            X=[]
            for key in dictionary[x].keys(): 
                X.append(key)
                y.append(len(dictionary[x][key]))
            if(len(y)<6):
                d={}
                d['type']='pie'
                data={}
                data['x-axis']=np.array(X)
                data['y-axis']=np.array(y)
                data['label']=[dataset.iloc[:,x].name,'Composition']
                d['info']=data
                res.append(d)
            d={}
            d['type']='bar'
            data={}
            data['x-axis']=np.array(X)
            data['y-axis']=np.array(y)
            data['label']=[dataset.iloc[:,x].name,'Composition']
            d['info']=data
            res.append(d)
        if(dataset.iloc[:,0].size<21):
            for x in dateL:
                if x not in rem:
                    for y in intL:
                        d1={}
                        d1['type']='bar'
                        data1={}
                        data1['x-axis']=dataset.iloc[:,x].values
                        data1['y-axis']=dataset.iloc[:,y].values
                        data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d1['info']=data1
                        res.append(d1)
                        d2={}
                        d2['type']='line'
                        data2={}
                        data2['x-axis']=dataset.iloc[:,x].values
                        data2['y-axis']=dataset.iloc[:,y].values
                        data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d2['info']=data2
                        res.append(d2)
            for x in intL:
                for y in intL:
                    if x is not y:
                        d1={}
                        d1['type']='bar'
                        data1={}
                        data1['x-axis']=dataset.iloc[:,x].values
                        data1['y-axis']=dataset.iloc[:,y].values
                        data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d1['info']=data1
                        res.append(d1)
                        if(np.corrcoef(dataset.iloc[:,x].values,dataset.iloc[:, y].values)[0,1]>0.95 or np.corrcoef(dataset.iloc[:,x].values,dataset.iloc[:,y].values)[0,1]<-0.95):
                            d2={}
                            d2['type']='line'
                            data2={}
                            data2['x-axis']=dataset.iloc[:,x].values
                            data2['y-axis']=dataset.iloc[:,y].values
                            data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d2['info']=data2
                            res.append(d2)
        elif(dataset.iloc[:,0].size<31):
            for x in dateL:
                if x not in rem:
                    for y in intL:
                        d1={}
                        d1['type']='bar'
                        data1={}
                        data1['x-axis']=dataset.iloc[:,x].values
                        data1['y-axis']=dataset.iloc[:,y].values
                        data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d1['info']=data1
                        res.append(d1)
                        d2={}
                        d2['type']='line'
                        data2={}
                        data2['x-axis']=dataset.iloc[:,x].values
                        data2['y-axis']=dataset.iloc[:,y].values
                        data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d2['info']=data2
                        res.append(d2)
            for x in intL:
                for y in intL:
                    if x is not y:
                        d1={}
                        d1['type']='bar'
                        data1={}
                        data1['x-axis']=dataset.iloc[:,x].values
                        data1['y-axis']=dataset.iloc[:,y].values
                        data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d1['info']=data1
                        if(np.corrcoef(dataset.iloc[:,x].values,dataset.iloc[:, y].values)[0,1]>0.95 or np.corrcoef(dataset.iloc[:,x].values,dataset.iloc[:,y].values)[0,1]<-0.95):
                            d2={}
                            d2['type']='line'
                            data2={}
                            data2['x-axis']=dataset.iloc[:,x].values
                            data2['y-axis']=dataset.iloc[:,y].values
                            data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d2['info']=data2
                            res.append(d2)
                            res.append(d1)
                        else:
                            d2={}
                            d2['type']='scatter'
                            data2={}
                            data2['x-axis']=dataset.iloc[:,x].values
                            data2['y-axis']=dataset.iloc[:,y].values
                            data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d2['info']=data2
                            res.append(d2)
                            res.append(d1)
        elif(dataset.iloc[:,0].size<101):
            for x in dateL:
                if x not in rem:
                    for y in intL:
                        d1={}
                        d1['type']='line'
                        data1={}
                        data1['x-axis']=dataset.iloc[:,x].values
                        data1['y-axis']=dataset.iloc[:,y].values
                        data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d1['info']=data1
                        res.append(d1)
            for x in intL:
                for y in intL:
                    if x is not y:
                        if(np.corrcoef(dataset.iloc[:,x].values,dataset.iloc[:, y].values)[0,1]>0.99 or np.corrcoef(dataset.iloc[:,x].values, dataset.iloc[:, y].values)[0,1]<-0.99):
                            d1={}
                            d1['type']='line'
                            data1={}
                            data1['x-axis']=dataset.iloc[:,x].values
                            data1['y-axis']=dataset.iloc[:,y].values
                            data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d1['info']=data1
                            res.append(d1) 
                        elif(np.corrcoef(dataset.iloc[:,x].values,dataset.iloc[:, y].values)[0,1]>0.95 or np.corrcoef(dataset.iloc[:,x].values,dataset.iloc[:,y].values)[0,1]<-0.95):
                            d1={}
                            d1['type']='line'
                            data1={}
                            data1['x-axis']=dataset.iloc[:,x].values
                            data1['y-axis']=dataset.iloc[:,y].values
                            data1['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d1['info']=data1
                            res.append(d1)
                            d2={}
                            d2['type']='scatter'
                            data2={}
                            data2['x-axis']=dataset.iloc[:,x].values
                            data2['y-axis']=dataset.iloc[:,y].values
                            data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d2['info']=data2
                            res.append(d2)
                        else:
                            d2={}
                            d2['type']='scatter'
                            data2={}
                            data2['x-axis']=dataset.iloc[:,x].values
                            data2['y-axis']=dataset.iloc[:,y].values
                            data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                            d2['info']=data2
                            res.append(d2)
        else:
            for x in dateL:
                if x not in rem:
                    for y in intL:
                        d2={}
                        d2['type']='scatter'
                        data2={}
                        data2['x-axis']=dataset.iloc[:,x].values
                        data2['y-axis']=dataset.iloc[:,y].values
                        data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d2['info']=data2
                        res.append(d2)
            for x in intL:
                for y in intL:
                    if x is not y:
                        d2={}
                        d2['type']='scatter'
                        data2={}
                        data2['x-axis']=dataset.iloc[:,x].values
                        data2['y-axis']=dataset.iloc[:,y].values
                        data2['label']=[dataset.iloc[:,x].name,dataset.iloc[:,y].name]
                        d2['info']=data2
                        res.append(d2)
        return res
class ShowGraph:
    def draw(res):
        for i in range(0,len(res)):
            d=res[i]
            if(d['type']=='pie'):
                DrawShapes.pie(d['info']['x-axis'], d['info']['y-axis'])
            elif(d['type']=='bar'):
                DrawShapes.bar(d['info']['x-axis'], d['info']['label'][0], d['info']['y-axis'], d['info']['label'][1])
            elif(d['type']=='line'):
                DrawShapes.line(d['info']['x-axis'], d['info']['label'][0], d['info']['y-axis'],  d['info']['label'][1])
            elif(d['type']=='scatter'):
                DrawShapes.scatter(d['info']['x-axis'], d['info']['label'][0], d['info']['y-axis'],  d['info']['label'][1])
    
    if __name__=="__main__":
        fileName=input()
        res=DecisionTree.chartType(fileName)
        draw(res)

"""
from scipy import stats
#a = np.array([ 2.71, 7.78, 20.58, 54.56, 148.56])
a = np.array([ 1,2,3,4,5,6,78])
score = stats.zscore(a)
count=0
score
for i in score:
    if(i<0):
        count=count+1
ratio=count/len(a)
ratio
"""