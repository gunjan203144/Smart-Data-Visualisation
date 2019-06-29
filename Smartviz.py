import pandas as pd
import itertools
from numpy import corrcoef
from math import log
from datetime import datetime as dt

class CreateChart:
    def __init__(self):

        self.conf = {
            'chart': {'zoomType': 'xy'},
            'credits': {'enabled': False},
            'plotOptions': {
                'series': {
                    'stacking': None,
                    'animation': False,
                    'cursor': 'pointer',
                    'allowPointSelect': True,
                    'turboThreshold': 0}
            },
            'legend': {
                'enabled': True,
                'squareSymbol': True,
                'symbolWidth': 12,
                'symbolRadius': 1,
                'itemStyle': {'fontSize': '10px'}},
            'xAxis':
                {
                    'type': 'linear',  # decided based on xAxis categories
                    'categories': [],  # categories to plot on x-axis
                    'labels': {'enabled': True},
                    'scrollbar': {'enabled': True},
                    'visible': True
                },
            'yAxis':
                {
                    'title': {'text': ' '},
                    'visible': True,
                    'type': 'linear',
                    'gridLineWidth': 0,
                    'labels': {'enabled': True},
                    'lineWidth': '1',
                    'tickLength': '1'
                },
            'template':
                {
                    'series': {
                        'askme': {'enabled': True},
                        'name': {'columnMapping': 1},  # series column

                        "dashStyle": {"columnMapping": 6},  # dash column
                        "type": {"columnMapping": 4},  # chart-type column

                        'data': {
                            'y': {'columnMapping': 2},  # y axis column
                            'x': {'columnMapping': 3},  # x axis column when using linear or datetime else removed
                            'name': {'columnMapping': 1}  # show series name on tooltip
                        }
                    }
                },
            'tooltip': {'shared': True, 'valueSuffix': '{point.tooltip1}'}
        }

    def dataType(self, meta):
        """
        meta=[
             {"colIndex":0,"colName":"month","colType":"Varchar"},
             {"colIndex":1,"colName":"AHT","colType":"Float","unit":"Seconds","type":"aC"}
        ]
        """
        
        
        """
        This function will segregate indices of columns on the basis of data types
        
        Numerical-> Float or Integer
        Categorical-> Varchar
        Temporal-> Date
        
        If data type is numerical then, it will return list of lists. Inner list will contain 
        indices of columns having similar units.
        
        Note: All numerical columns should necessarily have units.
        """
        dic2 = {}
        intL = []
        strL = []
        dateL = []

        for d in meta:
            # print(d)
            if d['colType'] == 'Varchar':
                strL.append(d['colIndex'])
            elif d['colType'] == 'Integer' or d['colType'] == 'Float':
                if d['unit'] in dic2.keys():
                    dic2[d['unit']].append(d['colIndex'])
                else:
                    li = [d['colIndex']]
                    dic2[d['unit']] = li

            elif d['colType'] == 'date':
                dateL.append(d['colIndex'])
        for i in dic2.values():
            intL.append(i)
        return intL, dateL, strL

    def create_config(self, x, y, type, series=None):
        self.conf["template"]["series"]["type"] = type
        self.conf["template"]["series"]["data"]["y"]["columnMapping"] = y
        self.conf["template"]["series"]["data"]["x"]["columnMapping"] = x
        self.conf["template"]["series"]["name"]["columnMapping"] = series



    def create_config_scatter(self, x, y, type, series=None, x_type="linear", y_type="linear"):
        print(x, y, type, series, y_type)
        """
        This separate function for scatter is because the change in scale in x-axis and y-axis
        will change the representation of scatter drastically. Therefore, in scatter scale of
        axes plays a major role in visualisation.
        
        So, we will keep that scale in which there is highest correlation.
        """
        self.conf["template"]["series"]["type"] = type
        self.conf["template"]["series"]["data"]["y"]["columnMapping"] = y
        self.conf["template"]["series"]["data"]["x"]["columnMapping"] = x
        self.conf["template"]["series"]["name"]["columnMapping"] = series
        self.conf["xAxis"]["type"] = x_type
        self.conf["xAxis"]["type"] = y_type
        
    def create_config_bubble(self, x, y, z, type, series=None, series2=None):
        """
        Bubble can show data of 4 columns directly.
        
        3 numerical columns will show the x-coordinate, y-coordinate, and size of bubble.
        1 categorical column can be represented with the help of colour of bubble.
        This function is used so that the Bubble chart can directly represent data of 4 
        columns
        """
        print(x, y, type, series,)
        self.conf["template"]["series"]["type"] = type
        self.conf["template"]["series"]["data"]["z"]["columnMapping"] = z
        self.conf["template"]["series"]["data"]["y"]["columnMapping"] = y
        self.conf["template"]["series"]["data"]["x"]["columnMapping"] = x
        self.conf["template"]["series"]["data"]["series2"]["columnMapping"] = series2
        self.conf["template"]["series"]["name"]["columnMapping"] = series

    #self.create_config_bubble(x=x, y=y, z=z, series=s, type="bubble")
    def get_interval_bins(dates_list):
        """
        This function will take list of temporal values and return list of dictionaries. It is
        called in transform_data_binning() method.
        
        Maximum length of output list will be 3.
        At 0th index dictionary having keys as Year and values as the list of indices of rows 
        at which the given key year is occurred.
        
        At 1st index dictionary having keys as Month and values as the list of indices of rows 
        at which the given key month is occurred.
        
        At 2nd index dictionary having keys as Day of week and values as the list of indices of rows 
        at which the given key day of week is occurred.
        """
        days = [[] for _ in range(7)]
        months = [[] for _ in range(12)]
        year_bins={str(i):[] for i in range(min(dates_list).year, max(dates_list).year+1)}
        index =0
        for date in dates_list:
            days[date.weekday()].append(index)
            months[date.month-1].append(index)
            year_bins[str(date.year)].append(index)
            index +=1 
        week_bins = {'Mondays' : days[0],
        'Tuesdays' : days[1],
        'Wednesdays' : days[2],
        'Thursdays' : days[3],
        'Fridays' : days[4],
        'Saturdays' : days[5],
        'Sundays' : days[6]} 
        
        month_bins ={'Jan' : months[0],
        'Feb' : months[1],
        'March' : months[2],
        'April' : months[3],
        'May' : months[4],
        'June' : months[5],
        'July' : months[6],
        'Aug' : months[7],
        'Sept' : months[8],
        'Oct' : months[9],
        'Nov' : months[10],
        'Dec': months[11]}
        return [{} if functools.reduce(lambda x,y: x + y , [ len(i) for i in year_bins.values()]) ==0 else year_bins, {} if functools.reduce(lambda x,y: x + y , [ len(i) for i in month_bins.values()]) ==0 else month_bins, {} if functools.reduce(lambda x,y: x + y , [ len(i) for i in week_bins.values()]) ==0 else week_bins]
    #def fill_years(year_bins):
    def bar_chart(self, result, meta):
        """
        This function is used to create all bar charts.
        
        """
        # conf = {
        #     "xAxis": None,
        #     "yAxis": None,
        #     "labels": None,
        #     "type": None
        # }
        intL, dateL, strL = meta
        temp = []
        ld = len(dateL)
        common = dateL + strL
        count = 0
        for x in common:
            for j in intL:
                for y in j:
                    self.create_config(x=x, y=y, type="bar")
                    """
                    Bar charts having one numerical or temporal column on x-axis and numerical
                    column on y-axis is created.
                    """
                    # temp.append({"type": "bar", "xAxis": x, "yAxis": y})
                    temp.append(self.conf)
                    if count < ld:
                        for series in strL:
                            if 1 < result[x].nunique() < 10:
                                # temp.append({"type": "bar", "xAxis": x, "yAxis": y, "series": series})
                                self.create_config(x=x, y=y, series=series, type="bar")
                                """
                                Bar charts having temoral column on x-axis, numerical column on
                                y-axis and categorical column as series are created.
                                Colour in stacked bar will represent unique categorical values and
                                it will be plotted according the corresponding one numerical column.
                                Threshold is 9 unique categorical values in categorical column.
                                """
                                temp.append(self.conf)
                            if 1 < result[series].nunique() < 10:
                                """
                                Bar charts having categorical column on x-axis, numerical column
                                on y-axis and temporal as series are created.
                                Colour in stacked bar will represent unique temporal values.
                                Threshold is 9 unique temporal values in temporal column.
                                """
                                self.create_config(x=series, y=y, series=x, type="bar")
                                temp.append(self.conf)
                                # temp.append({"type": "bar", "xAxis": series, "yAxis": y, "series": x})
                    else:
                        for s in strL:
                            if x < s:
                                """
                                Bar charts having categorical column on x-axis, numerical column
                                on y-axis and series as another categorical columns are plotted.
                                Which categorical column will be series and which will lie on
                                x-axis will be decided by the number of unique keys in that 
                                categorical column.
                                Categorical column having less number of distinct values will be
                                made series.
                                """
                                if result[s].nunique() > result[x].nunique():
                                    self.create_config(x=s, y=y, series=x, type="bar")
                                    temp.append(self.conf)
                                else:
                                    self.create_config(x=x, y=y, series=s, type="bar")
                                    temp.append(self.conf)

                if len(j) > 1:
                    """
                    Bar charts having Categorical or Temporal values on x-axis and 2 or more
                    numerical column having same units on y-axis are represented.
                    Scaling on y-axis should be decided on the basis of all data points in the 
                    numerical columns.
                    Colour of stacked bar will be used to represent the name of the numerical
                    column plotted in stacked bars.
                    """
                    self.create_config(x=x, y=j, type="bar")
                    temp.append(self.conf)
                    # temp.append({"type": "bar", "xAxis": x, "yAxis": j})
            count += 1
        """
        Note: Pie charts and Bar charts can also be plotted on 1 categorical or temporal
        column on the basis of frequency of each unique value.
        """
        return temp

    def line_chart(self, result, meta):
        intL, dateL, strL = meta
        temp = []
        common = strL + dateL
        for j in intL:
            for y in j:
                flag=0
                for x in dateL:
                    """
                    Line charts having temporal values on x-axis and numerical values on y-axis
                    are plotted.
                    """
                    self.create_config(x=x, y=y, type="line")
                    temp.append(self.conf)
                    for s in strL:
                        """
                        Line charts having temporal values on x-axis, numerical values on y-axis
                        and categorical values as series are plotted.
                        Colour of lines will be used to represent unique categorical values.
                        Threshold is 5 unique categorical values.
                        """
                        if (1 < result[s].nunique() < 6) and (result.shape[0] > (5 * result[s].nunique())):
                            self.create_config(x=x, y=y, series=s, type="line")
                            temp.append(self.conf)
                    if (flag == 0):
                        """
                        Line charts having temporal values on x-axis, numerical values on y-axis
                        and numerical values having same units as series are plotted. 
                        Colour of lines will tell the name of the numerical columns plotted
                        as line.
                        """
                        flag = 1
                        self.create_config(x=x, y=j, series=j, type="line")
                        temp.append(self.conf)
                for i in intL:
                    for x in i:
                        if x is not y:
                            for s in common:
                                """
                                Line charts having numerical values on x-axis, numerical values
                                on y-axis and categorical or temporal values as series are plotted.
                                Colour of lines will be used to represent unique categorical or
                                temporal values.
                                Threshold is 6 unique values in categorical or temporal column.
                                """
                                if (1 < result[s].nunique() < 6) and (result.shape[0] > (5 * result[s].nunique())):
                                    self.create_config(x=x, y=y, series=s, type="line")
                                    temp.append(self.conf)
        return temp

    def correlation(self, result, temp):
        result1 = 0.0
        result2 = 0.0
        result3 = 0.0
        result4 = 0.0
        """
        Last appended result will be popped and scale is changed so, that it can show highest
        correlation.
        """
        dic = temp.pop()
        x = dic['template']["series"]["data"]["x"]["columnMapping"]
        y = dic['template']["series"]["data"]["y"]["columnMapping"]
        s = dic["template"]['series']
        X_data = result.iloc[:, x]
        Y_data = result.iloc[:, y]
        # linear relation
        result1 = abs(corrcoef(X_data, Y_data)[0][1])
        if (min(X_data) > 0 and min(Y_data) > 0):
            logX = map(log, X_data)
            logY = map(log, Y_data)
            # logarithmic relation
            result2 = abs(corrcoef(X_data, logY)[0][1])
            # Exponential relation
            result3 = abs(corrcoef(logX, Y_data)[0][1])
            # power relation
            result4 = abs(corrcoef(logX, logY)[0][1])
        r = max(result1, result2, result3, result4)
        if (r == result2):
            self.create_config_scatter(x=x, y=y, series=s, type="scatter", y_type="logarithmic")
            temp.append(self.conf)
        elif (r == result3):
            self.create_config_scatter(x=x, y=y, series=s, type="scatter", x_type="logarithmic")
            temp.append(self.conf)
        elif (r == result4):
            self.create_config_scatter(x=x, y=y, series=s, type="scatter", x_type="logarithmic", y_type="logarithmic")
            temp.append(self.conf)
        else:
            self.create_config_scatter(x=x, y=y, series=s, type="scatter")
            temp.append(self.conf)
        return temp

    def scatter_chart(self, result, meta):
        intL, dateL, strL = meta
        temp = []
        common = strL + dateL
        if result.shape[0] > 40:
            for y in itertools.chain.from_iterable(intL):
                for x in itertools.chain.from_iterable(intL):
                    if x < y:
                        flag = 0
                        for s in common:
                            """
                            Scatter chart is plotted having numerical values on x-axis, numerical 
                            values on y-axis and series as temporal or categorical values.
                            Colour of dots will be used to represent unique categorical or
                            temporal values.
                            Threshold is 8 unique values.
                            """
                            if (1 < result[s].nunique() < 8) and (result.shape[0] > (4 * result[s].nunique())):
                                flag = 1
                                self.create_config(x=x, y=y, series=s, type="scatter")
                                temp.append(self.conf)
                                # call correlation here
                                temp = self.correlation(result, temp)
                        """
                        If there are more than 8 unique values in categorical or numerical 
                        column, or there is absence of temporal or categorical columns then
                        scatter chart with numerical values in x and y axes is plotted.
                        """
                        if flag == 0:
                            self.create_config(x=x, y=y, type="scatter")
                            temp.append(self.conf)
                            temp = self.correlation(result, temp)
                        """
                        Note:- Tool tip can be used to see the information of a dot in scatter 
                            clearly.
                        """
                            # call correlation here
        return temp

    def pie_chart(self, result, meta):
        intL, dateL, strL = meta
        temp = []
        common = intL + strL
        for y in itertools.chain.from_iterable(intL):
            for x in common:
                """
                Pie chart with one numerical column and one categorical or numerical column
                are plotted.
                Note: Pie charts and Bar charts can also be plotted on 1 categorical or temporal
                column on the basis of frequency of each unique value.
                """
                distinct = result[x].nunique()
                if (min(result[y]) > 0 and distinct < 11 and result.shape[0] == distinct):
                    self.create_config(x=x, y=y, type="pie")
                    temp.append(self.conf)
                """
                If data is too large having distinct values less than 11, then some agreggation  
                operation should be performed on numerical values to reduce size.
                AGG={ SUM, COUNT, AVG}
                """
                elif min(result[y]) > 0 and distinct < 11:
                    print('Operation on col_index ', y, ' w.r.t ', x)
    """
        meta=[
             {"colIndex":0,"colName":"month","colType":"Varchar"},
             {"colIndex":1,"colName":"AHT","colType":"Float","unit":"Seconds","type":"aC"}
    """
    def generate_transform_meta(transform_meta_list, index, result, coli):
        dic={}
        li=[]
        dic['colIndex']=0
        if(index==0):
            dic['colName']='Year'
        elif(index==1):
            dic['colName']='Month'
        elif(index==2):
            dic['colName']='Day of week'
        dic['colType']='String'
        li.append(dic)
        count=1
        for i in coli:
            dic1={}
            dic1['colIndex']=count
            dic1['colName']= result.iloc[:,i].name
            dic1['colType']='Float'
            li.append(dic1)
            count+=1
        transform_meta_list.append(li)
        return transform_meta_list
    
    def transform_data_binning(self, result, meta):
        """
        Use this function carefully.
        """
        intL, dateL, strL = meta
        bin_=[]
        transform_data=[]
        transform_meta_list=[]
        """
        This function will transform the data by operation SUM according to the
        binned temporal values as Year, Month and Day of Week. 
        get_interval_bin function will return list of dictionaries.
        """
        for i in dateL:
        """
        Date format should be DD/MM/YYYY.
        String is converted to datetime object and function get_interval_bins is called.
        """
            dates_list = [dt.strptime(date, '%d/%m/%Y') for date in result.iloc[:,i]]
            bin_=bin_ + self.get_interval_bins(dates_list)
        for i in bin_:
            count=0
            for j in i:
                temp=[]
                for x in j.keys():
                    li=[x]
                    dic={}
                    for num in itertools.chain.from_iterable(intL):
                        dic[num]=0
                    for k in j[x]:
                        for num in itertools.chain.from_iterable(intL):
                            dic[num]+=result.iloc[k,num]
                    li.extend(dic.values())
                    temp.append(li)
                transform_data.append(temp)
                transform_meta_list=generate_transform_meta(transform_meta_list, count, result, list(itertools.chain.from_iterable(intL)))
                count+=1
        """
        Transformed data is list of lists of lists.
        First inner list will contain the 0: lists of years, 1: lists of months, 2: lists of days of week.
        
        Second inner list will contain 0: which year, month or day of week, 
        1: Will contain dictionary having key as Numerical column index and value as 
        sum of that index according to the binned key. 
        [[['2011', {2: 213649381.0799999}], ['2012', {2: 223049087.68999997}], ['2013', {2: 241409373.22000012}], ['2014', {2: 245104266.73000026}], ['2015', {2: 247316886.61000058}], ['2016', {2: 171127318.73999986}]], [['Jan', {2: 117266923.78999995}], ['Feb', {2: 89581305.23999994}], ['March', {2: 118481762.83999999}], ['April', {2: 111983634.3}], ['May', {2: 115489848.6199999}], ['June', {2: 117529519.36999986}], ['July', {2: 142689067.48}], ['Aug', {2: 137888617.9499999}], ['Sept', {2: 97495373.12999997}], ['Oct', {2: 92858136.16000007}], ['Nov', {2: 94126637.1400001}], ['Dec', {2: 106265488.05000004}]], [['Monday', {2: 191393007.97000006}], ['Tuesday', {2: 194361594.31000027}], ['Wednesday', {2: 194647426.41000015}], ['Thursday', {2: 194674271.44999996}], ['Friday', {2: 193807802.35000026}], ['Saturday', {2: 189884251.8099999}], ['Sunday', {2: 182887959.76999977}]]]
        
        """
        return transform_data
        
        
    def draw_by_binning(self, result, meta):
        intL, dateL, strL = meta
        trial_index=intL[0][0]
        transform_data=[]
        temp=[]
        bin_=[self.get_interval_bins(i) for i in dateL]
        for i in bin_:
            for j in i:
                #for trial_index in itertools.chain.from_iterable(intL):
                x_list=[]
                y_list=[]
                for x in j.keys():
                    x_list.append(x)
                    sum_=0
                    for k in j[x]:
                        sum_+=result.iloc[k,trial_index]
                    y_list.append(sum_)
            # Bar or Line type 
            transform_data.append(x_list)
            transform_data.append(y_list)
            
                        
        
        
    def bubble_chart(self, result, meta):
        intL, dateL, strL = meta
        temp = []
        common = strL + dateL
        for y in itertools.chain.from_iterable(intL):
            for x in itertools.chain.from_iterable(intL):
                for z in itertools.chain.from_iterable(intL):
                    if x < y < z:
                        #flag = 0
                        for s in common:
                            """
                            Bubble chart with one numerical value on x-axis, another numerical
                            value on y-axis, another numerical values as size of bubble, and
                            categorical or temporal columns can be represented as colour of 
                            bubble or can be represented as it is only.
                            
                            Note:- Tool tip can be used to see the information of a bubble 
                            clearly.
                            
                            Refer to this link-> https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/demo/bubble/
                            """
                            self.create_config_bubble(x=x, y=y, z=z, series=s, type="bubble")
                            temp.append(self.conf)
                            """
                            The below part is incomplete, this part tries to show 2 categorical
                            or 1 categorical, 1 temporal and 3 numerical columns with the help of bubble chart.
                            Which categorical or temporal column should be directly shown and which
                            column should be shown through colours will decided by number of 
                            unique values in those columns.
                            """
                            for s2 in strL:
                                if s>s2:
                                   if result[s].nunique() > result[s2].nunique():
                                       self.create_config_bubble(x=s, y=y, series=x, type="bar")
                                       temp.append(self.conf) 
                                    
                                
    
    def heatmap(self, result, meta):
        """
        Use with caution null will be shown 
        data should be valid for all values in categories
        """
        intL, dateL, strL = meta
        temp = []
        """
        Heat map with categorical values on x-axis, temporal values on y-axis and numerical 
        values as Scale of colours is shown.
        Refer to this link:- https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/demo/heatmap/
        """
        for x in strL:
            for y in dateL:
                for z in itertools.chain.from_iterable(intL):
                    self.create_config(x=x, y=y, series=z, type="heatmap")
                    temp.append(self.conf)

        
if __name__ == "__main__":
    request = [["NONE", "NORTH AMERICA", 447672951.33], ["SOFIA,KARLIE", "NORTH AMERICA", 229131176.98],
               ["WILLIAMS,WADE", "NORTH AMERICA", 182377426.82], ["LESINSKI,LAWRENCE", "NORTH AMERICA", 136120305.29],
               ["ROSARIO PEREZ", "NORTH AMERICA", 127528219.49], ["HOFFMAN,KARLIE", "NORTH AMERICA", 105577862.36],
               ["RAMIREZ PONCE,OLAF ROGELIO", "NORTH AMERICA", 76393870.55], ["NONE", "EUROPE", 69702563.32],
               ["GOMEZ GONZALEZ,RAUL", "NORTH AMERICA", 69584286.74],
               ["WADE,CHRISTOPHER", "NORTH AMERICA", 53631225.63], ["PARKER JOHN", "NORTH AMERICA", 48498174.37],
               ["WANG,HELEN", "ASIA", 47199872.59], ["CHAFFIN, MELISSA", "NORTH AMERICA", 43708416.28],
               ["KOSTRZEWSKI,MACIEJ", "EUROPE", 43485463.56], ["KARBOWSKI,ROBERT", "NORTH AMERICA", 43366562.44],
               ["BLAS ESPINOZA,DAMARIS ANAHI", "NORTH AMERICA", 43314877.29],
               ["BERG, ROLAND", "NORTH AMERICA", 43227581.44], ["ROBERTSON, DALE", "NORTH AMERICA", 43195758.93],
               ["DAWN VERELLE", "NORTH AMERICA", 42536307.11], ["WALDSCHMIDT,MICHAEL", "NORTH AMERICA", 39026166.8],
               ["JOEL CARDENAS", "NORTH AMERICA", 37939651.2], ["NONE", "ASIA", 37751212.06],
               ["MOONEY, PETER", "NORTH AMERICA", 37019099.91], ["XU,QIAN", "ASIA", 35855355.31],
               ["HOFFMAN, KARLIE", "NORTH AMERICA", 35849534.68], ["TOONE,ANTHONY", "NORTH AMERICA", 35566036.34],
               ["OGG,STACIE", "NORTH AMERICA", 35078686.64], ["SANDENOR,SUSANNE", "EUROPE", 34004833.72],
               ["MEDRANO ALVARADO,CESAR EDUARDO", "NORTH AMERICA", 31456646.09],
               ["ZUNIGA PEREZ,JOSE ALFREDO", "NORTH AMERICA", 31202470.54],
               ["CANO,MIRIAM", "NORTH AMERICA", 29908211.83], ["TREJO MARTINEZ,LUCIANO", "NORTH AMERICA", 29896983.6],
               ["LOVE,JACOB", "NORTH AMERICA", 29304355.93],
               ["ARREGUIN ORTEGA,AMELIA JIMENA", "NORTH AMERICA", 29193120.19],
               ["HINKLE, CHERYL", "NORTH AMERICA", 28553426.22], ["ARAIZA LARA,SAMUEL", "NORTH AMERICA", 27583733.61],
               ["ANGUIANO SUAREZ,FERNANDO IVAN", "NORTH AMERICA", 27368181.03],
               ["KIM GOSIAK", "NORTH AMERICA", 26958958.61], ["TAMMY BAUER", "NORTH AMERICA", 26670520.72],
               ["AMANDA THORNE", "NORTH AMERICA", 26605971.37], ["MP", "NORTH AMERICA", 25869767.2],
               ["MACDONALD, SCOTT", "NORTH AMERICA", 23604544.08], ["KNAPP LESLIE", "NORTH AMERICA", 23296039.4],
               ["KNIGHT DIANA", "NORTH AMERICA", 23178177.67], ["JOSE LUIS VAZQUEZ", "NORTH AMERICA", 22155369.03],
               ["LOSIN,PAUL", "NORTH AMERICA", 22137655.26], ["MARGIE MCCLURE", "NORTH AMERICA", 21510403.88],
               ["GITTENS,JAMES", "NORTH AMERICA", 20840234.27], ["METALDYNE STOREROOM", "NORTH AMERICA", 20660283.35],
               ["ZHANG,VINCENT", "ASIA", 20001870.75], ["ARMANDO VILLALOBOS", "NORTH AMERICA", 18556363.71],
               ["SHERRIE CLEMENS", "NORTH AMERICA", 18055420.19], ["O'BRIEN,JON", "NORTH AMERICA", 17588447.25],
               ["MIKE CHRISTAL", "NORTH AMERICA", 17286969.04], ["SCHNEIDER LINDA M.", "NORTH AMERICA", 16467806.68],
               ["XU,JUN", "ASIA", 15898066.15], ["GORYL,MARCIN", "EUROPE", 15652991.37],
               ["BRAD SPAULDING", "NORTH AMERICA", 15635348.95], ["SOFIA, KARLIE", "NORTH AMERICA", 15084836.95],
               ["SANTOS,JULIANE", "SOUTH AMERICA", 14849511.82], ["MADIGAN,JAMES", "NORTH AMERICA", 14537271.66],
               ["GUZMAN CONTRERAS,ANGEL", "NORTH AMERICA", 14367422.38],
               ["BACERDO, MAUI", "NORTH AMERICA", 14311329.18], ["INKONG,SORAYA", "ASIA", 13493032.91],
               ["ROSZKOWSKI,LAURA", "NORTH AMERICA", 13331706.66], ["TAVERA,CARLA", "NORTH AMERICA", 12930953.84],
               ["DE FREITAS,SIDINEI", "SOUTH AMERICA", 12919726.05], ["MARATHE,PRASHANT", "INDIA", 12766463.09],
               ["LEATHERMAN, JASON", "NORTH AMERICA", 12756902.59], ["SALTER,JOHN", "NORTH AMERICA", 12677524.43],
               ["MARYCARMEN INDA", "NORTH AMERICA", 11658007.39], ["NANCY AMICANGELO", "NORTH AMERICA", 11463508.36],
               ["HEATHER JONES", "NORTH AMERICA", 11239711.93], ["JUSTIN BURKHOUSE", "NORTH AMERICA", 10776513.86],
               ["AMARAL,ELISA", "SOUTH AMERICA", 10770818.14], ["SONI,KAMLESHKUMAR", "INDIA", 10660513.48],
               ["VALDES VITE,EDGAR HIRAM", "NORTH AMERICA", 10652121.02],
               ["VILLANUEVA GAONA,MARIA FERNANDA", "NORTH AMERICA", 10572186.88],
               ["BENITEZ LOPEZ,ERICKA ELIZABETH", "NORTH AMERICA", 10475785.89],
               ["NIYOMCHAN,RUNGNAPA", "ASIA", 10436652.46], ["DIANA KNIGHT", "NORTH AMERICA", 10399679.86],
               ["YANG,PAUL", "ASIA", 10222952.1], ["Catalog Purchases", "NORTH AMERICA", 9919668.71],
               ["DROZDOWICZ, MICHAEL", "NORTH AMERICA", 9789314.55],
               ["CANO HERNANDEZ,MIRIAM DEL ROSARIO", "NORTH AMERICA", 9697594.05],
               ["NO BUYER ASSIGNED", "NORTH AMERICA", 9696792.91],
               ["GARCIAPICAZO,ARIADNA TERESA", "NORTH AMERICA", 9677362.75],
               ["SHARON HOOMES", "NORTH AMERICA", 9480970.62], ["KEVIN TERRELL", "NORTH AMERICA", 9432799.45],
               ["AHN JUNHEE", "ASIA", 9417774.65], ["FROMER, JULIE", "NORTH AMERICA", 9415531.95],
               ["FREITAS,SIDINEI", "SOUTH AMERICA", 9287024.52], ["ROSZKOWSKI, LAURA", "NORTH AMERICA", 9269424.71],
               ["WADE, CHRISTOPHER", "NORTH AMERICA", 9149312.84], ["NANCY GREENAWALT", "NORTH AMERICA", 9011279.93],
               ["DEBORAH AUDINO", "NORTH AMERICA", 8981381.71], ["MOTA, VANESSA", "NORTH AMERICA", 8242290.66],
               ["WILLWANG", "ASIA", 8225279.46], ["LAURA,SALAS", "NORTH AMERICA", 8128490.05],
               ["KAMSTRA, BENNETT", "NORTH AMERICA", 7833230.69], ["BLANKENMYER,TRACI", "NORTH AMERICA", 7726252.61],
               ["ROBERTO MENDOZA", "NORTH AMERICA", 7526922.73], ["VERELLEN,DAWN", "NORTH AMERICA", 7521000.62],
               ["PARKER JOHN", "EUROPE", 7430354.46], ["TORRES,DANYA LUCILA", "NORTH AMERICA", 7310765.1],
               ["MIELNICZEK,KATARZYNA", "EUROPE", 7237965.76], ["QUINN,BERNARD", "NORTH AMERICA", 7200549.1],
               ["MOLCZYK, JOSEPH", "NORTH AMERICA", 7192845.95], ["ANGEL YAGER", "NORTH AMERICA", 7085496.39],
               ["ROBIN CALLA", "NORTH AMERICA", 6974610.13], ["VERELLEN DAWN", "EUROPE", 6933235.35],
               ["BAKER, JOHN", "NORTH AMERICA", 6870663.81], ["JULIE VERSCHAGE", "NORTH AMERICA", 6671126.72],
               ["KETELHUT,TONYA", "NORTH AMERICA", 6381195.02], ["LORA SHIELDS", "NORTH AMERICA", 6224723.54],
               ["CANDY UHL", "NORTH AMERICA", 6121116.43], ["CHLON,CHRISTOPHER", "NORTH AMERICA", 6010472.93],
               ["ANDREW SCOTT", "NORTH AMERICA", 5797807.06], ["ENGELMANN,VERONIKA", "EUROPE", 5748797.47],
               ["GONZALEZ LOPEZ,GRASIELA", "NORTH AMERICA", 5199035.01],
               ["FENNER,TOWNSHEND", "NORTH AMERICA", 5174401.36], ["ANANTHA, RAM", "NORTH AMERICA", 4901613.25],
               ["KNAPP LESLIE", "EUROPE", 4881419.12], ["KOSLAKIEWICZ,MARYJANE", "NORTH AMERICA", 4762838.82],
               ["LAMBRECHT,SHARON", "NORTH AMERICA", 4511043.34], ["MCCOOL,BRIAN", "EUROPE", 4458575.75],
               ["SCHNEIDER LINDA M.", "EUROPE", 4410088.66], ["EUZENES,MATHILDE", "NORTH AMERICA", 4086691.27],
               ["VERELLEN DAWN", "NORTH AMERICA", 4079206.96], ["WEISHÃ¤UPL, JANA", "EUROPE", 3906283.72],
               ["LIQUIA, MICHAEL", "NORTH AMERICA", 3807384.02], ["ZUEHLKE, LINDSAY", "NORTH AMERICA", 3575718.17],
               ["MAYELA LUEVANO", "NORTH AMERICA", 3274780.38], ["MANOLE,ALEXANDRU", "EUROPE", 3239436],
               ["CALEY, CARRIE", "NORTH AMERICA", 3224861.42], ["SHELLY KIM", "ASIA", 3215494.34],
               ["COSTER,JOHN", "NORTH AMERICA", 3129044.93], ["NONE", "SOUTH AMERICA", 3058323.98],
               ["HILDA ALMANZA", "NORTH AMERICA", 3029978.87], ["BELL, CHRIS", "NORTH AMERICA", 3005976.62],
               ["DESHMUKH,SACHIN", "INDIA", 2956354.79], ["K,VENKATESH", "INDIA", 2931922.09],
               ["LOOSVELT, MICHAEL", "NORTH AMERICA", 2922914.81], ["ZHOU,BOURNE", "ASIA", 2918223.22],
               ["SER", "NORTH AMERICA", 2787483.38], ["JAIME RODRIGUEZ", "NORTH AMERICA", 2661782.84],
               ["RW - TOOLING", "NORTH AMERICA", 2615376.52], ["SPANGLE, MELANIE", "NORTH AMERICA", 2556330.97],
               ["SZUSTAK,SANDRA", "EUROPE", 2411586.44], ["WONGPILAIWAT,NUCHSARA", "ASIA", 2377120.35],
               ["SOPHIE WU", "ASIA", 2376876.29], ["AMBRIZ,DULCE MARIA", "NORTH AMERICA", 2376310.09],
               ["ERIKSSON,PERNILLA", "EUROPE", 2375950.2], ["GONZALEZ,NANCY", "NORTH AMERICA", 2359916.63],
               ["JINNAWUT,PIMOLRAT", "ASIA", 2256788.66], ["GONZALEZ TREJO,ROSA MARIA", "NORTH AMERICA", 2234531.81],
               ["STACY SMITH", "NORTH AMERICA", 2106792.95], ["BELL,CHRIS", "NORTH AMERICA", 2042567.14],
               ["SUSAN STRIDER", "NORTH AMERICA", 2012466.03], ["GUERRA,OMAR GABRIEL", "NORTH AMERICA", 1999094.4],
               ["SZCZYPEK,KATARZYNA", "EUROPE", 1966731.67], ["ANGUIAN SUAREZ,FERNANDO", "NORTH AMERICA", 1955687.6],
               ["KNIGHT DIANA", "EUROPE", 1855072.77], ["HUCUL,KYLE", "NORTH AMERICA", 1847147.36],
               ["JAVI LOPEZ", "EUROPE", 1843417.92], ["JOSE MANUEL MORELL", "EUROPE", 1839858.54],
               ["NUNES,GABRIEL", "SOUTH AMERICA", 1826272.27], ["VICTOR SANCHEZ", "NORTH AMERICA", 1812411.15],
               ["HERNANDEZ,KATTYA DANIELA", "NORTH AMERICA", 1811720.57], ["XU,JUN", "EUROPE", 1810570.2],
               ["LYLE,TIMOTHY", "NORTH AMERICA", 1803574.73], ["HORÁKOVÁ, MARTINA", "UNKNOWN", 1798525.06],
               ["SALAS TERRONES,LAURA ALICIA", "NORTH AMERICA", 1688214.89],
               ["WILSON,BRIAN", "NORTH AMERICA", 1667696.47], ["R,PAVITHRA", "INDIA", 1663518.66],
               ["LESINSKI,LARRY", "NORTH AMERICA", 1632622.72], ["SCHAEFER,TONYA", "NORTH AMERICA", 1622319.04],
               ["DEB LAWTON", "NORTH AMERICA", 1616068.24], ["PUNTRAP,MANOP", "ASIA", 1611873.91],
               ["DO NOT USE", "EUROPE", 1610614.64], ["WILLIAMS, WADE", "NORTH AMERICA", 1584247.5],
               ["SCHULER,MATTHEW", "NORTH AMERICA", 1575075.04], ["JAIKAEW,KITTICHAI", "ASIA", 1573477.1],
               ["DAVID BENEDE", "EUROPE", 1494984.76], ["BLAZO, PATRICK", "NORTH AMERICA", 1485521.8],
               ["BLANK BUYER", "NORTH AMERICA", 1482648.32],
               ["HERNANDEZ ALCALA,LORENA ANAIS", "NORTH AMERICA", 1482583.22],
               ["JENNY BURNS", "NORTH AMERICA", 1421886.74], ["GORYL,MAREK", "EUROPE", 1370452.44],
               ["CARDOSO,OSMAR", "SOUTH AMERICA", 1352431.33], ["DONG,ERIC", "ASIA", 1285651.42],
               ["LASORSA SALCEDO,NICOLA JOSE", "NORTH AMERICA", 1283659.21],
               ["LEE,JANUARY", "NORTH AMERICA", 1234200.48], ["ANITA KIMBRELL", "NORTH AMERICA", 1230768.63],
               ["GRAJEDA ORTIZ,ANDRES", "NORTH AMERICA", 1229422.45], ["KIM STEUDLER", "NORTH AMERICA", 1229029.06],
               ["OSCAR LAMAS", "EUROPE", 1216501.81], ["HEAGLE, KELLY", "NORTH AMERICA", 1209429.25],
               ["WATKINS, SHAWN", "NORTH AMERICA", 1145913.31], ["WEISHÄUPL, JANA", "UNKNOWN", 1133614.21],
               ["PEREGRINA MELLADO,EVA MARIA", "NORTH AMERICA", 1132586.16],
               ["HEIDI BREHMER", "NORTH AMERICA", 1131922.05], ["SANDENOR,SUSANNE", "ASIA", 1117928.97],
               ["MEDINA LOPEZ,RAUL ALEJANDRO", "NORTH AMERICA", 1104782.47],
               ["HOAG, BRENT", "NORTH AMERICA", 1093351.51], ["KONJA,NICHOLAS", "NORTH AMERICA", 1089890.49],
               ["SILVA,FELIPE", "SOUTH AMERICA", 1055648.22], ["NO BUYER ASSIGNED", "ASIA", 1053492.17],
               ["FOWLER, KALEB", "NORTH AMERICA", 1053145.34], ["TAYLOR,CHARLES", "NORTH AMERICA", 1051021.43],
               ["KELLY KRUEGER", "NORTH AMERICA", 1035155.63],
               ["VALADES MORENO,JOSE JORGE", "NORTH AMERICA", 1031596.1], ["KIM GYLAND", "NORTH AMERICA", 1028479.55],
               ["PATIL,SOMNATH", "INDIA", 1025515.61], ["SMITH,DAVID", "NORTH AMERICA", 1023869.78],
               ["KMIECIŃSKI,OSKAR", "EUROPE", 1023492.39], ["GIDDENS KEITH", "EUROPE", 1022924.68],
               ["JACKSON,CHRISTA", "NORTH AMERICA", 1001802.37], ["ROBERT PETERSON", "NORTH AMERICA", 960789.64],
               ["CHRIS WOZNIAK", "NORTH AMERICA", 951370.68], ["TABAKA LARRY", "NORTH AMERICA", 939541.46],
               ["RYAN SMITH", "NORTH AMERICA", 935050.69], ["AMBRIZ ROZALEZ,DULCE MARIA", "NORTH AMERICA", 900085],
               ["ORTIZ SOTO,JAVIER", "NORTH AMERICA", 894970.51], ["KARL RASMUSSEN", "NORTH AMERICA", 894274.3],
               ["CHAVEZ MUNOZ,JUAN FRANCISCO", "NORTH AMERICA", 885441.55], ["SHIN,SUN HA", "NORTH AMERICA", 882168.68],
               ["GRANADOS,MONTSERRAT", "NORTH AMERICA", 873966.17], ["ONICA, LINDSAY", "NORTH AMERICA", 833814.54],
               ["SUE SHIVERS", "NORTH AMERICA", 829334.88], ["SOFIA,KARLIE", "EUROPE", 811236.67],
               ["JULIE BELANGER", "NORTH AMERICA", 798879.47], ["NONE", "INDIA", 793627.23], ["戴晓松", "ASIA", 787514],
               ["SCHNEIDER,LINDA", "NORTH AMERICA", 786935], ["CAITLIN CANADA", "NORTH AMERICA", 783176.01],
               ["JOEY PINTADO", "NORTH AMERICA", 776200.72],
               ["SIERRA WITRAGO,JESSICA MONSERRAT", "NORTH AMERICA", 748123.4],
               ["VERELLEN, DAWN", "NORTH AMERICA", 746955], ["MARINA VIVEROS,ANA FABIOLA", "NORTH AMERICA", 742103.58],
               ["KENDRA MCCLURE", "NORTH AMERICA", 739733.97], ["CHEN,CALVIN", "EUROPE", 724697.04],
               ["ENNIS, SHANE", "NORTH AMERICA", 719399.84], ["NONE", "UNKNOWN", 702922.62],
               ["DA SILVA,FELIPE", "SOUTH AMERICA", 694323.24],
               ["PANIAGUA VIDEGARAY,AUGUSTO CESAR", "NORTH AMERICA", 689310.72],
               ["SCHUPP, WILLIAM", "NORTH AMERICA", 684706.4], ["CHEN,CALVIN", "ASIA", 682997.11],
               ["MARTINOT,ELISA CRISTINA", "NORTH AMERICA", 676990.84],
               ["HERNANDEZ ALCALA,LORENA ANAIS", "EUROPE", 672928.93], ["ZHANG,VINCENT", "EUROPE", 638178.39],
               ["SANSARE,PANKAJ", "INDIA", 631866.09], ["KELLEY DAY", "NORTH AMERICA", 629339.83],
               ["JAMES HASSLER", "NORTH AMERICA", 620712.48], ["JOHNSON, ELIJAH", "NORTH AMERICA", 614789.73],
               ["MCGREGOR,WILLIAM", "EUROPE", 609399.02], ["LEDYARD AMY J.", "NORTH AMERICA", 608188.58],
               ["STEVE HINCHLIFFE", "NORTH AMERICA", 588377.46], ["GUO,HAOJIE", "ASIA", 584952.64],
               ["AMANDA MENEGHINI", "NORTH AMERICA", 584888.96], ["KENNEDY, STEVEN", "NORTH AMERICA", 584301.65],
               ["SCOTT GROSSINGER", "NORTH AMERICA", 576577.15], ["GILL,GURPREET", "NORTH AMERICA", 576321.5],
               ["GORYL,MARCIN", "ASIA", 573718.85], ["MANOLO MONTES", "EUROPE", 567041.45],
               ["K,VENKATESH", "SOUTH AMERICA", 565469.13], ["PAULET,ADRIEN", "EUROPE", 560017.08],
               ["KMIECI?SKI,OSKAR", "EUROPE", 553269.82], ["GONZALEZ ROSAS,MAURICIO", "NORTH AMERICA", 537724.92],
               ["SHIELDS LORA E.", "EUROPE", 515053.52], ["REF", "NORTH AMERICA", 511395.83],
               ["AMBER DAI", "ASIA", 501151.09], ["SONI,KAMLESHKUMAR", "ASIA", 493722.23],
               ["RAMIREZ PONCE,OLAF ROGELIO", "ASIA", 486890.91], ["INKONG,SORAYA", "EUROPE", 481278.9],
               ["RAY,SHISHIR", "INDIA", 468838.35], ["ZHAO,FRANCO", "ASIA", 462174.03],
               ["NIYOMCHAN,RUNGNAPA", "EUROPE", 460768.68], ["DETTMAR, MICHAELA", "UNKNOWN", 460733.41],
               ["LOPEZ RODRIGUEZ,ALEJANDRA", "NORTH AMERICA", 459728.72], ["GOMEZ GONZALEZ,RAUL", "ASIA", 455375.33],
               ["ZILIO,ANGELA", "SOUTH AMERICA", 453662.64], ["BENOIT,AMY", "NORTH AMERICA", 450945.62],
               ["ZACH FISHAW", "NORTH AMERICA", 440198.96], ["HAMILTON, MARK", "NORTH AMERICA", 437983.21],
               ["AHUMADA ANGEL,MARIA MANUELA", "NORTH AMERICA", 418215.55],
               ["HORÃ¡KOVÃ¡, MARTINA", "EUROPE", 411321.76], ["MARTINOT,ELISA CRISTINA", "SOUTH AMERICA", 401682.86],
               ["LEDYARD AMY J.", "EUROPE", 400145.41], ["SUE KOELLER", "NORTH AMERICA", 386346.18],
               ["NICHOLSON,SARAH", "NORTH AMERICA", 378150.39], ["BARNUM,BRANDON", "NORTH AMERICA", 373428.2],
               ["Âº†Âº©", "ASIA", 371801.45], ["SOFIA,KARLIE", "INDIA", 352500],
               ["MONTES, GUILLERMINA", "NORTH AMERICA", 348954.11], ["PARKER,JOHN", "NORTH AMERICA", 342730],
               ["IBARRA MARQUEZ,RAMON", "NORTH AMERICA", 339215.77], ["BLAZO,PATRICK", "NORTH AMERICA", 335182.01],
               ["MELVIN, AMELIA", "NORTH AMERICA", 329051.74], ["DONNA BOYD", "NORTH AMERICA", 327498.25],
               ["QUINN, BERNARD", "NORTH AMERICA", 325873], ["LONG, STACEY", "NORTH AMERICA", 318973.67],
               ["TRENT GARBER", "NORTH AMERICA", 318036.38], ["RAMIREZ PONCE,OLAF ROGELIO", "EUROPE", 313941.15],
               ["JOSE MANUEL VIRUES", "EUROPE", 305365.05], ["ALEJANDRO GARGALLO", "EUROPE", 301038.08],
               ["SZEJN,ALDONA", "EUROPE", 292171.55], ["CHOUDHARI,RAJESH", "INDIA", 291237.83],
               ["XU,QIAN", "EUROPE", 280744.88], ["DE FREITAS,SIDINEI", "INDIA", 278644.31],
               ["WURMLINGER, TREVOUR", "NORTH AMERICA", 278328.11], ["MARKWORT,ERIK", "NORTH AMERICA", 265061.8],
               ["TREJO MARTINEZ,LUCIANO", "ASIA", 258219.24], ["SHANNON GREENE", "NORTH AMERICA", 255379.86],
               ["DETTMAR, MICHAELA", "EUROPE", 252093.98], ["CHRISTOPHER WADE", "NORTH AMERICA", 249600],
               ["YALAMAKUR,RAGHUNATH", "EUROPE", 246558.35], ["OUDSHOORN,MARK", "EUROPE", 234181.4],
               ["LARA PEREZ,DANIEL ALBERTO", "NORTH AMERICA", 228402.15],
               ["OUELLETTE,BRIAN", "NORTH AMERICA", 226506.56], ["WONGPILAIWAT,NUCHSARA", "EUROPE", 223576.55],
               ["POULARD,GEOFFREY", "EUROPE", 223510.01], ["LARSON, MICHAEL", "NORTH AMERICA", 221771.14],
               ["SANDRA FERGUSON", "NORTH AMERICA", 214571.62], ["KAVITAKE,PRAKASH", "INDIA", 212320.19],
               ["KELLY DUCKETT", "NORTH AMERICA", 208985.82], ["CRUZ-ALVARADO, EDER", "NORTH AMERICA", 200069.86],
               ["KASSANDRA ZURCHER", "NORTH AMERICA", 198656.88], ["MAIORANO, CHRISTOPHER", "NORTH AMERICA", 197301.66],
               ["ROSE, JOSEPH", "NORTH AMERICA", 190574], ["JUDY SCHLAF", "NORTH AMERICA", 189202.16],
               ["GAVIN BURSTALL", "NORTH AMERICA", 187866.6], ["SZWEJK,JAMI", "NORTH AMERICA", 187790.17],
               ["PALOMA GRAU", "EUROPE", 183418.65], ["RANDY AMUNDSON", "NORTH AMERICA", 182040.53],
               ["WONGPILAIWAT,NUCHSARA", "NORTH AMERICA", 180208.17], ["MANOLE,ALEXANDRU", "NORTH AMERICA", 175797.2],
               ["BERNARD QUINN", "NORTH AMERICA", 175134], ["GOULET,MICHAEL", "NORTH AMERICA", 174815.44],
               ["NANCY PENG", "ASIA", 171548.12], ["TREJO MARTINEZ,LUCIANO", "EUROPE", 170092.66],
               ["ANGUIAN SUAREZ,FERNANDO", "ASIA", 162113.06], ["OEHLER, KARINA", "UNKNOWN", 158596.33],
               ["NO BUYER ASSIGNED", "SOUTH AMERICA", 157382.81], ["ZHANG,SELINA", "ASIA", 154179.44],
               ["BONANCIO,AMANDA", "SOUTH AMERICA", 152559.48],
               ["GARCIA DE LA O,LUIS ANGEL", "NORTH AMERICA", 151892.9], ["EASH, ANDY", "NORTH AMERICA", 151508.59],
               ["SIMPSON,ROBERT", "NORTH AMERICA", 150750], ["CANELAS,AMANDA", "SOUTH AMERICA", 146957.67],
               ["JEREMY YODER", "NORTH AMERICA", 145445.14], ["ARAIZA LARA,SAMUEL", "ASIA", 145172.51],
               ["AMARAL,ELISA", "INDIA", 144320.75], ["STREIT, NICHOLAS", "NORTH AMERICA", 142971.46],
               ["FENNER,TOWNSHEND", "EUROPE", 141741.28], ["ANITA BRYANT", "NORTH AMERICA", 141046.32],
               ["MYERS, DEREK", "NORTH AMERICA", 141035.67], ["ROBERTO ANDRADE", "EUROPE", 137086.26],
               ["MARKPHAN,JIRAMET", "ASIA", 136302.77], ["WADE,CHRISTOPHER", "EUROPE", 133410.49],
               ["DANDE,PRASHANT", "INDIA", 132470.97], ["HARMEYER, NICK", "NORTH AMERICA", 129024.11],
               ["SCHAEFER,TONYA", "EUROPE", 128937.24], ["SEILHEIMER, MARITA", "UNKNOWN", 128289.8],
               ["OSCAR AGUILAR", "NORTH AMERICA", 127796.27], ["CINDY LU", "EUROPE", 127710.79],
               ["CULLIFER,JEAN", "NORTH AMERICA", 123628.48], ["BEACHEM, STEVE", "NORTH AMERICA", 119023.25],
               ["KINEL, ROBERT", "NORTH AMERICA", 118913.14], ["MENDOZA PINON,EVER", "NORTH AMERICA", 118556.03],
               ["VELAZQUEZ AGUIRRE,JOSE ISRAEL", "NORTH AMERICA", 118474.1], ["KATHY PACK", "NORTH AMERICA", 116988.9],
               ["SMITH STACY R.", "EUROPE", 116865.78], ["OEHLER, KARINA", "EUROPE", 116091.68],
               ["RODRIGO ROMERO", "EUROPE", 115860.23], ["ELAINE LIU", "ASIA", 111445.76],
               ["PEREZ, JUAN", "NORTH AMERICA", 108135.3], ["STACHULSKI, THOMAS", "NORTH AMERICA", 106952.32],
               ["MIKE WATKINS", "NORTH AMERICA", 106142.7], ["MORALES TELLEZ,RICARDO", "NORTH AMERICA", 105648.32],
               ["MACDONALD,SCOTT", "NORTH AMERICA", 105192.79], ["SANTOS,JULIANE", "INDIA", 104743.78],
               ["NO BUYER ASSIGNED", "INDIA", 104716.32], ["MANOLE,ALEXANDRU", "ASIA", 103569.04],
               ["EVA ESTEVE", "EUROPE", 103426.05], ["OUELLETTE, BRIAN", "NORTH AMERICA", 101866.57],
               ["KUJAWA,KAMILA", "EUROPE", 101069.84], ["EISENMANN, VIKTORIA", "UNKNOWN", 98581.83],
               ["GOULET,MICHAEL", "EUROPE", 92940.6], ["TRYON, SHAWN", "NORTH AMERICA", 92851.41],
               ["GOMEZ,RAUL", "NORTH AMERICA", 91466.74], ["INKONG,SORAYA", "NORTH AMERICA", 88062.17],
               ["BROGDON, THOMAS", "NORTH AMERICA", 88034.27], ["HINCHLIFFE STEPHEN F.", "EUROPE", 86680.87],
               ["SMITH, DAN", "NORTH AMERICA", 82099], ["PASCUAL OLLETA", "EUROPE", 81112.68],
               ["SONI,KAMLESHKUMAR", "SOUTH AMERICA", 77869.52], ["JULIO ABAD", "EUROPE", 76827.46],
               ["TREJO,LUCIANO", "NORTH AMERICA", 72906.74], ["HERNANDEZ,GEMA", "NORTH AMERICA", 67321.98],
               ["PACO SALIDO", "EUROPE", 66348.43], ["WANG,DOREEN", "ASIA", 63425.56],
               ["WOJIHOSKI, JEROME", "NORTH AMERICA", 63416.2], ["ROBERT WEIX", "NORTH AMERICA", 61727.06],
               ["PACO RIBERA", "EUROPE", 61385.99], ["GORYL,MAREK", "ASIA", 60852.2],
               ["CICILIAN, BRIAN", "NORTH AMERICA", 58083.68], ["JACKI RADOSTA", "NORTH AMERICA", 57802.11],
               ["COTTER, DAN", "NORTH AMERICA", 57735.02], ["ZUNIGA,JOSE ALFREDO", "NORTH AMERICA", 57687.41],
               ["MOTE, TUSHAR", "NORTH AMERICA", 56610.25], ["RHODES, JEFFREY", "NORTH AMERICA", 56025],
               ["RAMIREZ,OLAF ROGELIO", "NORTH AMERICA", 55330.81], ["KONKOLY,MARLENE", "NORTH AMERICA", 55221.6],
               ["ROSE, ROBERT", "NORTH AMERICA", 52872.82], ["VALDES VITE,EDGAR HIRAM", "ASIA", 51630],
               ["ARMSTRONG, MICHAEL", "NORTH AMERICA", 50950], ["KARACA,DORUK", "EUROPE", 49840.98],
               ["HOMERO GALLEGOS", "NORTH AMERICA", 48634.65], ["METALDYNE", "NORTH AMERICA", 47955.86],
               ["GOMEZ GONZALEZ,RAUL", "EUROPE", 46508.04], ["NORTH, ANDREW", "NORTH AMERICA", 46404.38],
               ["INMA PASCUAL", "EUROPE", 45810.31], ["MACDONALD PATRICIA", "NORTH AMERICA", 45738.24],
               ["PRANGE, JEFFREY", "NORTH AMERICA", 45071.73], ["EISENMANN, VIKTORIA", "EUROPE", 44286.34],
               ["PEREGRINA,EVA MARIA", "NORTH AMERICA", 43206.42], ["CARVALHO,SUELEN", "SOUTH AMERICA", 43116.16],
               ["ALLEN, STEVE", "NORTH AMERICA", 42703.75], ["VILLA, YESENIA", "NORTH AMERICA", 42112.74],
               ["MARCHAND,VALERIE", "NORTH AMERICA", 40437], ["张弩", "ASIA", 40295.4],
               ["BARNUM,BRANDON", "EUROPE", 40000], ["FRANCISCO PILES", "EUROPE", 39464.59],
               ["PENNELL, PAUL", "NORTH AMERICA", 38085.96], ["MORRISH, ROBERT", "NORTH AMERICA", 37182],
               ["ANGUIANO,FERNANDO IVAN", "NORTH AMERICA", 36827.34], ["BOWEN, KALEN", "NORTH AMERICA", 36143.37],
               ["BRUINSMA, JERROLD", "NORTH AMERICA", 36125.26], ["DAVID SPICER", "NORTH AMERICA", 35717.13],
               ["JOSE BRAVO", "EUROPE", 35288.43], ["POTIER,EVANDRO", "SOUTH AMERICA", 34630.3],
               ["WARNER, MATTHEW", "NORTH AMERICA", 34452.79], ["SZEJN,ALDONA", "ASIA", 33924.48],
               ["HOFFMAN,KARLIE", "EUROPE", 33603.63], ["JOAN PEREZ (CALIDAD)", "EUROPE", 33051.62],
               ["MEDRANO,CESAR EDUARDO", "NORTH AMERICA", 31644.36], ["CODE JY NOT FOUND", "NORTH AMERICA", 31404.08],
               ["SANTIAGO, JOSE", "NORTH AMERICA", 30987.69], ["RICHARD HARTZ", "NORTH AMERICA", 30655.46],
               ["CRAFT,JOSHUA", "NORTH AMERICA", 30500], ["JOSE APARICIO", "EUROPE", 30468.21],
               ["BLAS ESPINOZA,DAMARIS ANAHI", "EUROPE", 30464.9], ["KOLIS, TIM", "NORTH AMERICA", 30272.23],
               ["LOPATKA, KENNETH", "NORTH AMERICA", 30149.1], ["DAVE REINKE", "NORTH AMERICA", 28638.13],
               ["XU,JUN", "NORTH AMERICA", 28549.15], ["CHRISMAN DON L.", "EUROPE", 28501.93],
               ["NO BUYER ASSIGNED", "EUROPE", 28221.68], ["PACO BARTUAL", "EUROPE", 27559.64],
               ["SILVIA BARRIOS", "EUROPE", 27103.15], ["ZAYAC,JAMES", "NORTH AMERICA", 26852.03],
               ["HILDEBRANDT, CHAD", "NORTH AMERICA", 26633.22], ["GAO,FRANK", "ASIA", 26612.19],
               ["ÁÉÃÂ?¶‰ºÜ", "ASIA", 26209.5], ["BLAS ESPINOZA,DAMARIS ANAHI", "ASIA", 25911.33],
               ["WALDSCHMIDT,MICHAEL", "SOUTH AMERICA", 25644.32], ["RUMANO,FLAVIA", "NORTH AMERICA", 25000],
               ["ARREGUIN,AMELIA JIMENA", "NORTH AMERICA", 24714.37], ["CHAVEZ MUNOZ,JUAN FRANCISCO", "ASIA", 24309.66],
               ["STEVENS,MELISSA", "NORTH AMERICA", 24098.8], ["SANDENOR,SUSANNE", "NORTH AMERICA", 23082.53],
               ["SEILHEIMER, MARITA", "EUROPE", 21891.49], ["SOTO NIETO,JORGE PABLO", "NORTH AMERICA", 21667.17],
               ["DONG,ERIC", "EUROPE", 21314], ["KOZAK, GREGORY", "NORTH AMERICA", 20936.8],
               ["ARAIZA LARA,SAMUEL", "EUROPE", 20420.42], ["MOSMANN, SYLVIA", "EUROPE", 20321.8],
               ["‰?ÅËÈ?", "ASIA", 20125.27], ["VICENTE PAU", "EUROPE", 20115.18],
               ["ENGELMANN,VERONIKA", "NORTH AMERICA", 19776.71], ["KARLA STERWALD", "NORTH AMERICA", 19703.8],
               ["SAWVEL, CHRISTOPHER", "NORTH AMERICA", 19109.2], ["JUAN MANUEL JAIMES", "EUROPE", 18592.88],
               ["FRAPPIER, JOE", "NORTH AMERICA", 18307.98], ["PATRICIA MACDONALD", "NORTH AMERICA", 17841.21],
               ["GORYL,MARCIN", "NORTH AMERICA", 17792.21], ["COTTON, JOSEPH", "NORTH AMERICA", 17629.16],
               ["KLEIN, JEFFREY", "NORTH AMERICA", 17568.15], ["ZHAO,FRANCO", "EUROPE", 17135.24],
               ["MEDRANO ALVARADO,CESAR EDUARDO", "ASIA", 16959.81], ["FAAS, NICOLE", "EUROPE", 16795.51],
               ["KELLER, TOBIAS", "UNKNOWN", 16651.49], ["XU,QIAN", "NORTH AMERICA", 16498.85],
               ["Æ´ÆÆ¾", "ASIA", 15935.24], ["JINNAWUT,PIMOLRAT", "NORTH AMERICA", 15654],
               ["ARAIZA,SAMUEL", "NORTH AMERICA", 15532.52], ["BEARD, JACOB", "NORTH AMERICA", 15447],
               ["LAWRENCE,LESINSKI", "NORTH AMERICA", 14878.44], ["BORIOLO,DIEGO", "SOUTH AMERICA", 14667.76],
               ["FRAKES,JOHN", "NORTH AMERICA", 14476.56], ["ZHANG,VINCENT", "NORTH AMERICA", 13470.03],
               ["NIYOMCHAN,RUNGNAPA", "NORTH AMERICA", 13455.73], ["MADIGAN,JAMES", "EUROPE", 13440],
               ["NGARNSIRI,THITIPONG", "ASIA", 13007.68], ["JOSE ANTONIO DIEGO", "EUROPE", 12556.35],
               ["MELTON,VERCY", "NORTH AMERICA", 12547.3], ["BROWNLOW, MONICA", "NORTH AMERICA", 12392.89],
               ["BOHACEK, ROBERT", "NORTH AMERICA", 12319.6], ["GRAJEDA ORTIZ,ANDRES", "EUROPE", 12000],
               ["SZALEWICZ, KEVIN", "NORTH AMERICA", 11957], ["MOSMANN, SYLVIA", "UNKNOWN", 11571.39],
               ["BLAIR,KIMBERLY", "NORTH AMERICA", 11080], ["LOSIN,PAUL", "SOUTH AMERICA", 10809.24],
               ["WILLIAMS,WADE", "ASIA", 10497.75], ["NOT ASSIGNED", "NORTH AMERICA", 10293.15],
               ["ARREGUIN ORTEGA,AMELIA JIMENA", "ASIA", 10241.17], ["CHAVEZ MUNOZ,JUAN FRANCISCO", "EUROPE", 10201.04],
               ["PALAZZOLO,RENEE", "NORTH AMERICA", 9795], ["METALDYNE POWERTRAIN COMPONENT", "NORTH AMERICA", 9158.36],
               ["DE FREITAS,SIDINEI", "NORTH AMERICA", 9000], ["HENDRICKS, ROBERT", "NORTH AMERICA", 8947.73],
               ["LIDIA LOPEZ", "EUROPE", 8802.49], ["GU,RICHARD", "EUROPE", 8721.46],
               ["CRISTINA GUILLOT", "EUROPE", 8669.82], ["FAAS, NICOLE", "UNKNOWN", 8355.09],
               ["BARDELLI, DINO", "NORTH AMERICA", 8241], ["LITKE, EDWARD", "NORTH AMERICA", 8118.19],
               ["MILLER, DENNIS", "NORTH AMERICA", 8109.34], ["GARCIA CONTRERAS,ISABEL", "NORTH AMERICA", 8054.18],
               ["SALDIVAR, JOSE", "NORTH AMERICA", 8016.5], ["LORETO SANTAMA", "EUROPE", 7991.22],
               ["CARDOSO,OSMAR", "INDIA", 7958.91], ["KELLER, TOBIAS", "EUROPE", 7888.84],
               ["COSTELLO,SCOTT", "NORTH AMERICA", 7800], ["BENENATI, TRACEY", "NORTH AMERICA", 7691.67],
               ["PURCHASING DEPARTMENT", "NORTH AMERICA", 7437.15], ["JAVIER RODRIGUEZ", "EUROPE", 7427.14],
               ["MEXICO", "EUROPE", 7388.48], ["JOE HEADLEY", "NORTH AMERICA", 7371.98],
               ["JAVI APARICI", "EUROPE", 7257.83], ["SCHÃ¶NER, MICHAEL", "EUROPE", 6865.06],
               ["GORANG, AARON", "NORTH AMERICA", 6858.07], ["CANELAS,AMANDA", "INDIA", 6837.33],
               ["GRIFFIN, TARA", "NORTH AMERICA", 6349.2], ["Ä¸È²", "ASIA", 6305.07],
               ["LUEDKE, MATTHEW", "NORTH AMERICA", 6237], ["CARVALHO,SUELEN", "INDIA", 6195.56],
               ["CASTILLO, PATRICIA M.", "NORTH AMERICA", 6182.5], ["QUOTING", "NORTH AMERICA", 6129.93],
               ["WANG,HELEN", "EUROPE", 6066.28], ["KREBS, LISA", "NORTH AMERICA", 5854.2],
               ["HOFFMAN,KARLIE", "ASIA", 5840], ["MIELNICZEK,KATARZYNA", "ASIA", 5794.73],
               ["MIRAMONTES, JORGE", "NORTH AMERICA", 5551.5], ["GITTENS,JAMES", "SOUTH AMERICA", 5376.48],
               ["BULMER, NICOLE", "EUROPE", 5055.55], ["GIDDENS KEITH", "NORTH AMERICA", 4990],
               ["HOOKER, COREY", "NORTH AMERICA", 4800], ["WOZNIAK, JENNIFER", "NORTH AMERICA", 4800],
               ["BULMER, NICOLE", "UNKNOWN", 4695.96], ["SZCZYPEK,KATARZYNA", "UNKNOWN", 4654],
               ["BENITEZ LOPEZ,ERICKA ELIZABETH", "EUROPE", 4620.09], ["ANTONIO LEYVA", "EUROPE", 4459.07],
               ["BUHLER PRINCE INC.", "NORTH AMERICA", 4357.6], ["LAUREN DOLES", "NORTH AMERICA", 4350],
               ["GARCIAPICAZO,ARIADNA TERESA", "EUROPE", 4233], ["DAVID KROLL", "NORTH AMERICA", 4144.29],
               ["SEAN VANALSTINE", "NORTH AMERICA", 4104.15], ["VILLANUEVA GAONA,MARIA FERNANDA", "EUROPE", 3825],
               ["APTE,CHAITANYA", "INDIA", 3817.44], ["MORENO RODRIGUEZ,RODOLFO", "NORTH AMERICA", 3808],
               ["TOMMY DELAY", "NORTH AMERICA", 3660.84], ["KOBER, ARNOLD", "NORTH AMERICA", 3606.36],
               ["HLADISH, ED", "NORTH AMERICA", 3564], ["MORENO,MARK", "NORTH AMERICA", 3525.36],
               ["MAKSIMOVSKI,BORCE", "NORTH AMERICA", 3521.8], ["王学伟", "ASIA", 3513.23],
               ["ZHOU,BOURNE", "EUROPE", 3426.25], ["KOSTRZEWSKI,MACIEJ", "ASIA", 3181.43],
               ["MARINA VIVEROS,ANA FABIOLA", "ASIA", 2991.56], ["GUANDIQUE, CHRISTIAN", "NORTH AMERICA", 2986],
               ["JAIKAEW,KITTICHAI", "NORTH AMERICA", 2855.21], ["CHLON,CHRISTOPHER", "ASIA", 2853.36],
               ["LEMISH, TIMOTHY", "NORTH AMERICA", 2852], ["MARATHE,PRASHANT", "NORTH AMERICA", 2832.47],
               ["SNELLENBERGER KATHLEEN", "EUROPE", 2736.8], ["F01", "NORTH AMERICA", 2732.25],
               ["DIGRAZIA, THOMAS", "NORTH AMERICA", 2687.5], ["ÈÔÀËÂ?", "ASIA", 2575.05], ["郭攀", "ASIA", 2512],
               ["LARA PEREZ,DANIEL ALBERTO", "ASIA", 2467.52], ["CRISTINA NOVILLO", "EUROPE", 2462.35],
               ["WILLIAMS,WADE", "SOUTH AMERICA", 2434.31], ["KLEBER, MATTHEW", "NORTH AMERICA", 2417],
               ["F36", "NORTH AMERICA", 2371.4], ["EDGE RITE TOOLS INC.", "NORTH AMERICA", 2280],
               ["PLATZER, JOHN", "NORTH AMERICA", 2064], ["ORTIZ SOTO,JAVIER", "EUROPE", 1953.53],
               ["DESHMUKH,SACHIN", "NORTH AMERICA", 1951.3], ["HILL, EDWIN", "NORTH AMERICA", 1880],
               ["SMITH, DANIEL", "NORTH AMERICA", 1856], ["KNIGHT,DIANA", "NORTH AMERICA", 1802.78],
               ["PUNTRAP,MANOP", "EUROPE", 1786.32], ["ARREGUIN ORTEGA,AMELIA JIMENA", "EUROPE", 1758.78],
               ["ÈÉ?ÊÎÄ", "ASIA", 1729.75], ["GARCIA CONTRERAS,ISABEL", "ASIA", 1625.28],
               ["COSTER, JOHN", "NORTH AMERICA", 1620.8], ["GLUECKERT, DAVID", "NORTH AMERICA", 1490],
               ["JAIKAEW,KITTICHAI", "EUROPE", 1488.88], ["É­Æ", "ASIA", 1476.99],
               ["SCHÖNER, MICHAEL", "UNKNOWN", 1476.14], ["GU,RICHARD", "NORTH AMERICA", 1342.92],
               ["NICHOLSON,SARAH", "ASIA", 1307.23], ["BUCHMILLER, LISA", "EUROPE", 1280.79],
               ["TORRES,DANYA LUCILA", "EUROPE", 1172.8], ["GUO,HAOJIE", "EUROPE", 1127.35],
               ["OEZKAYA,OKTAY", "EUROPE", 1070.64], ["ZUNIGA PEREZ,JOSE ALFREDO", "ASIA", 1067.95],
               ["DEBUSSCHER, ERIC", "NORTH AMERICA", 1055], ["WANG,HELEN", "INDIA", 1054.99],
               ["DAVIS, EISHUN", "NORTH AMERICA", 1028], ["SUE GONZALES", "NORTH AMERICA", 1000],
               ["MURILLO, GENARO", "NORTH AMERICA", 990.46], ["ANDY KAUN", "NORTH AMERICA", 956.87],
               ["ROSZKOWSKI,LAURA", "SOUTH AMERICA", 921.65], ["ANGUIAN SUAREZ,FERNANDO", "EUROPE", 910.69],
               ["WILSON,BRIAN", "SOUTH AMERICA", 809.33], ["O'BRIEN,JON", "SOUTH AMERICA", 698.23],
               ["SHUFF, RANDALL", "NORTH AMERICA", 675], ["VELAZQUEZ AGUIRRE,JOSE ISRAEL", "ASIA", 668.14],
               ["LEDYARD,AMY", "NORTH AMERICA", 634.9], ["TORRES,DANYA LUCILA", "ASIA", 626.85],
               ["BLAS ESPINOZA,DAMARIS ANAHI", "INDIA", 622], ["PACO MARTINEZ LATORRE", "EUROPE", 609.43],
               ["陈艳", "ASIA", 575.37], ["ORTIZ SOTO,JAVIER", "ASIA", 571.62],
               ["BURLINGAME,BRIANNA", "NORTH AMERICA", 567.74], ["PAN GUO", "ASIA", 520.94],
               ["SZYBOWICZ,PATRICK", "NORTH AMERICA", 472.85], ["ZHANG,VINCENT", "INDIA", 464.42],
               ["SALTER,JOHN", "SOUTH AMERICA", 457.4], ["BOCTOR, ALBAIR", "NORTH AMERICA", 452.4],
               ["LAMBRECHT,SHARON", "SOUTH AMERICA", 438.39], ["INKONG,SORAYA", "INDIA", 434.17],
               ["IMLAY, MICHELLE", "NORTH AMERICA", 410], ["COMBER, THOMAS", "NORTH AMERICA", 386.86],
               ["HOFFMAN,KARLIE", "SOUTH AMERICA", 384.55], ["DONG,ERIC", "NORTH AMERICA", 358.4],
               ["*** DO NOT USE ***", "NORTH AMERICA", 351.67], ["KARLSSON,MARIE", "EUROPE", 215.24],
               ["ROSZKOWSKI,LAURA", "INDIA", 214.55], ["MARKPHAN,JIRAMET", "EUROPE", 202.47],
               ["HERNANDEZ,GEMA", "SOUTH AMERICA", 195.93], ["DA SILVA,FELIPE", "INDIA", 176.29],
               ["VELAZQUEZ AGUIRRE,JOSE ISRAEL", "EUROPE", 169.22], ["LOSIN,PAUL", "UNKNOWN", 148.95],
               ["MARINA VIVEROS,ANA FABIOLA", "EUROPE", 134.74], ["AHUMADA ANGEL,MARIA MANUELA", "ASIA", 100.2],
               ["丁菲", "ASIA", 96.82], ["DULANEY HOLLY B.", "NORTH AMERICA", 85.99],
               ["WANG,HELEN", "NORTH AMERICA", 82.05], ["LOPEZ,ALEJANDRA", "NORTH AMERICA", 54.35],
               ["FRANCISCO BARTUAL (ALMACEN)", "EUROPE", 18.25], ["GAMALIEL MARTINEZ", "NORTH AMERICA", 0],
               ["CANDY UHL - MLS BUYER CODE", "NORTH AMERICA", -978.13]]

    meta = [{"colIndex": 0, "colName": "buyer", "colType": "Varchar", "unit": None, "type": "aD"},
            {"colIndex": 1, "colName": "region", "colType": "Varchar", "unit": None, "type": "aD"},
            {"colIndex": 2, "colName": "SUM OF SPEND AMOUNT", "colType": "Float", "unit": "$", "type": "aM"}]

    resultScatter = [["Catalog Purchases",282808442.24,8347648],["ROSARIO PEREZ",213788241.74,347337],["WILLIAMS,WADE",183376903.08,261260],["SOFIA,KARLIE",180486364.7,327047],["LESINSKI,LAWRENCE",107083947.03,441390],["HOFFMAN,KARLIE",106541696.54,130886],["JOEL CARDENAS",99667430.55,634060],["UNKNOWN",87530547.26,2062461],["RAMIREZ PONCE,OLAF ROGELIO",72710297.91,2639633],["GOMEZ GONZALEZ,RAUL",59861194.06,3496388],["CATALOG PURCHASE",54937904.62,None],["WANG,HELEN",45228567.92,111132],["ARMANDO VILLALOBOS",45048230.46,174474],["SANDENOR,SUSANNE",41622707.69,188017],["MOONEY, PETER",40698943.6,1130315],["WALDSCHMIDT,MICHAEL",39136778.16,809514],["BLAS ESPINOZA,DAMARIS ANAHI",38848926.89,1066540],["MP",38818251.91,632865],["CHAFFIN, MELISSA",36569756.68,2011914],["ROBERTSON, DALE",36353972.8,437590],["TOONE,ANTHONY",35555161.34,172272],["BERG, ROLAND",35539828.65,774436],["OGG,STACIE",35493534.17,870075],["UNSPECIFIED",34641601.91,245570],["DIANA KNIGHT",30962518.06,141033],["CANO,MIRIAM",30148882.1,556260],["HOFFMAN, KARLIE",30131367.31,46602],["KARBOWSKI,ROBERT",29008539.16,864364],["XU,QIAN",28358645.31,691184],["DAWN VERELLE",27088044.48,13050],["ARAIZA LARA,SAMUEL",26922721.97,1525046],["GITTENS,JAMES",26913693.67,391836],["MEDRANO ALVARADO,CESAR EDUARDO",25138892.01,2672267],["JOSE LUIS VAZQUEZ",24107278.52,105931],["KIM GOSIAK",23824676.75,236145],["ZUNIGA PEREZ,JOSE ALFREDO",23813988.16,1437770],["MACDONALD, SCOTT",23666189,475880],["WADE,CHRISTOPHER",22886293.95,83220],["AMANDA THORNE",22764934.72,191055],["HINKLE, CHERYL",22601705.13,1831340],["ARREGUIN ORTEGA,AMELIA JIMENA",22471304.59,517035],["ANGUIANO SUAREZ,FERNANDO IVAN",22083245.2,1805009],["TREJO MARTINEZ,LUCIANO",21204621.11,1463324],["PARKER JOHN",20604779.56,197430],["ROSZKOWSKI,LAURA",19254004.46,200096],["LOSIN,PAUL",18683747.8,399123],["VILLANUEVA GAONA,MARIA FERNANDA",17931269.62,16098],["O'BRIEN,JON",17638233.36,1515605],["ZHANG,VINCENT",17542814,957300],["TAMMY BAUER",17420678.89,505275],["METALDYNE STOREROOM",17073231.44,798225],["GORYL,MARCIN",16957245.62,360774],["XU,JUN",15137506.72,242285],["SHERRIE CLEMENS",14730701.27,207219],["KNAPP LESLIE",13329813.53,821310],["DE FREITAS,SIDINEI",13215655.57,498557],["SALTER,JOHN",12821915.91,190671],["MADIGAN,JAMES",12525789.2,244775],["LOVE,JACOB",12239192.83,251639],["MIKE CHRISTAL",12096167.69,654112],["SANTOS,JULIANE",11743387.05,519435],["INKONG,SORAYA",11712499.99,616097],["SONI,KAMLESHKUMAR",11664528.01,256382],["BRAD SPAULDING",11406278.24,686355],["NO BUYER ASSIGNED",11405180.5,194817],["AMARAL,ELISA",11384830.77,311729],["NIYOMCHAN,RUNGNAPA",11083747.55,745577],["HEATHER JONES",11037415.29,696402],["TAVERA,CARLA",10725443.8,553713],["LEATHERMAN, JASON",10582812.45,938496],["BAKER, JOHN",9953073.65,417073],["SCHNEIDER LINDA M.",9789938.67,781847],["WILLWANG",9765630.78,399630],["GARCIAPICAZO,ARIADNA TERESA",9747624.75,596604],["NANCY AMICANGELO",9716282.17,244344],["KNIGHT DIANA",9496953.58,4960],["KEVIN TERRELL",9245735.01,21075],["KETELHUT,TONYA",8874938.45,133079],["SHARON HOOMES",8485701.66,75510],["DEBORAH AUDINO",7924245.7,447725],["MARATHE,PRASHANT",7894999.88,106213],["VERELLEN DAWN",7845724.35,3875],["JUSTIN BURKHOUSE",7690291.95,260050],["MARYCARMEN INDA",7670579.11,4020],["TORRES,DANYA LUCILA",7630194.75,248415],["VALDES VITE,EDGAR HIRAM",7395925.55,10932],["AHN JUNHEE",7358256.63,5210],["BACERDO, MAUI",7354181.01,160436],["MIELNICZEK,KATARZYNA",7334523.16,256091],["ROBERTO MENDOZA",6993560.53,1534867],["MANOLE,ALEXANDRU",6695648.65,20880],["BENITEZ LOPEZ,ERICKA ELIZABETH",6648837.64,720513],["NANCY GREENAWALT",6494432.52,188170],["CHLON,CHRISTOPHER",6019726.3,34894],["GUZMAN CONTRERAS,ANGEL",5992527,370571],["FREITAS,SIDINEI",5917699.02,192864],["ENGELMANN,VERONIKA",5813906.7,8755],["MOLCZYK, JOSEPH",5764632.72,331863],["ROBIN CALLA",5675568.1,288271],["DROZDOWICZ, MICHAEL",5493821.73,305512],["ROSZKOWSKI, LAURA",5473889.67,136349],["GONZALEZ LOPEZ,GRASIELA",5422254.46,93609],["ANGEL YAGER",5237252.73,74800],["LORA SHIELDS",5047977.09,203676],["FROMER, JULIE",5035443.87,381105],["KOSLAKIEWICZ,MARYJANE",4985354.98,6275],["BLANKENMYER,TRACI",4845910.98,303750],["CANDY UHL",4828673.38,323640],["YANG,PAUL",4720965.82,35454],["MOTA, VANESSA",4657288.24,170093],["BENOIT,AMY",4654200.4,3834],["JULIE VERSCHAGE",4620125.42,147039],["WADE, CHRISTOPHER",4555798.09,3411],["LAMBRECHT,SHARON",4520960.95,80805],["MCCOOL,BRIAN",4465547.63,23974],["EUZENES,MATHILDE",4109562.19,141917],["KAMSTRA, BENNETT",4062222.65,271142],["GORYL,MAREK",4011070.94,25269],["LIQUIA, MICHAEL",3807498.22,217137],["ANANTHA, RAM",3768013.35,51772],["ZHOU,BOURNE",3703481.97,5210],["K,VENKATESH",3520972.29,78922],["GRAJEDA ORTIZ,ANDRES",3505631.88,24428],["COSTER,JOHN",3378077.62,35049],["DESHMUKH,SACHIN",3375139.3,60423],["VICTOR SANCHEZ",3364571.58,105660],["BELL, CHRIS",3315939.6,137486],["CALEY, CARRIE",3212339.05,126450],["HILDA ALMANZA",3032366.52,100235],["BELL,CHRIS",2975987.21,68324],["JAIME RODRIGUEZ",2870873.57,23171],["HERNANDEZ ALCALA,LORENA ANAIS",2832943.13,4308],["WONGPILAIWAT,NUCHSARA",2793235.82,111511],["FENNER,TOWNSHEND",2703923.26,64353],["PATRICIA MACDONALD",2652732.67,17747],["MAYELA LUEVANO",2628893.36,74191],["BLAZO, PATRICK",2587735.22,25715],["LOOSVELT, MICHAEL",2578205.55,44851],["AMBRIZ,DULCE MARIA",2497378.01,116135],["SOPHIE WU",2495488.08,94690],["LAURA,SALAS",2427455.1,49755],["SER",2318764.6,45787],["ZUEHLKE, LINDSAY",2282663.13,76644],["GONZALEZ TREJO,ROSA MARIA",2234531.81,103092],["RW - TOOLING",2197678.43,117670],["SANSARE,PANKAJ",2176270.9,7966],["ANGUIAN SUAREZ,FERNANDO",2166855.28,138672],["WILSON,BRIAN",2116368.76,35584],["VERELLEN,DAWN",2099395.21,2856],["SZUSTAK,SANDRA",1962271.83,41082],["CANO HERNANDEZ,MIRIAM DEL ROSARIO",1879487.03,48231],["STACY SMITH",1863971.33,55573],["BARNUM,BRANDON",1846681.21,1836],["CARDOSO,OSMAR",1840791.25,4783],["HERNANDEZ,KATTYA DANIELA",1811720.57,30144],["KONJA,NICHOLAS",1775827.76,25011],["LEE,JANUARY",1761623.24,23362],["CHEN,CALVIN",1684419.92,1995],["SCHULER,MATTHEW",1681004.31,38560],["MARGIE MCCLURE",1673464.59,159522],["MANOLO MONTES",1657679.86,60720],["DEB LAWTON",1631982.68,90720],["GONZALEZ,NANCY",1618121.27,165452],["JOSE MANUEL MORELL",1611036.22,159975],["JAVI LOPEZ",1604305.82,408675],["JAIKAEW,KITTICHAI",1602955.09,10455],["WILLIAMS, WADE",1584247.5,452],["SPANGLE, MELANIE",1557916.67,150352],["SHELLY KIM",1477382.32,116425],["BLANK BUYER",1440391.98,11185],["SUSAN STRIDER",1419301.12,48500],["SCHAEFER,TONYA",1415496.72,27454],["LESINSKI,LARRY",1299490.05,8385],["HOAG, BRENT",1297120.23,72132],["DAVID BENEDE",1272941.29,77850],["KIM STEUDLER",1263285.66,7915],["JENNY BURNS",1260066.74,10145],["PEREGRINA MELLADO,EVA MARIA",1235029.16,41061],["GOULET,MICHAEL",1214894.81,1092],["MEDINA LOPEZ,RAUL ALEJANDRO",1118912.86,15555],["SHIN,SUN HA",1088712.72,24487],["TABAKA LARRY",1076287.35,14215],["SMITH,DAVID",1054819.78,12078],["DONG,ERIC",1047339.05,5832],["KMIECIŃSKI,OSKAR",1032796.18,32811],["GIDDENS KEITH",1022924.68,50160],["OSCAR LAMAS",965353.81,247980],["CHRIS WOZNIAK",951370.68,6900],["CHAVEZ MUNOZ,JUAN FRANCISCO",919952.25,72456],["HEIDI BREHMER",914889.21,3180],["PUNTRAP,MANOP",889592.08,5790],["FOWLER, KALEB",886476.64,50748],["LEDYARD AMY J.",884871.49,20715],["GILL,GURPREET",880849.22,4435],["ONICA, LINDSAY",839723.19,32061],["NUNES,GABRIEL",832536.65,89401],["JULIE BELANGER",798879.47,37930],["KELLY KRUEGER",795115.15,57885],["MARTINOT,ELISA CRISTINA",787156.54,39912],["HINCHLIFFE STEPHEN F.",776365.98,7785],["GUO,HAOJIE",767269.21,2294],["KARL RASMUSSEN",762317.17,22815],["MARINA VIVEROS,ANA FABIOLA",751522.44,8127],["JINNAWUT,PIMOLRAT",750582.34,70476],["SIERRA WITRAGO,JESSICA MONSERRAT",750563.4,33252],["DA SILVA,FELIPE",744398.8,3006],["GONZALEZ ROSAS,MAURICIO",670189.62,6657],["BLAZO,PATRICK",668987.28,8648],["WATKINS, SHAWN",639970.93,42414],["PAULET,ADRIEN",639337.04,6009],["ORTIZ SOTO,JAVIER",630291.08,3479],["KELLEY DAY",629339.83,3115],["KIM GYLAND",623331.39,63823],["JOHNSON, ELIJAH",614789.73,885],["GUERRA,OMAR GABRIEL",611338.51,30540],["MACDONALD PATRICIA",587877.97,2065],["ZHAO,FRANCO",573962.67,5432],["KMIECI?SKI,OSKAR",554998.8,12886],["SHIELDS LORA E.",530626.95,33525],["NICHOLSON,SARAH",510747.61,2907],["ENNIS, SHANE",506945.08,206162],["HEAGLE, KELLY",502424.13,15000],["GRANADOS,MONTSERRAT",485874.82,25359],["RAY,SHISHIR",468838.35,71289],["ZACH FISHAW",438149.28,10798],["REF",436453.45,16702],["SUE SHIVERS",435941.23,7815],["ZILIO,ANGELA",432754.6,6013],["Âº†Âº©",425309.82,29160],["AHUMADA ANGEL,MARIA MANUELA",418315.75,8813],["JACKSON,CHRISTA",416197.01,40869],["SZEJN,ALDONA",415413.24,3580],["RYAN SMITH",392666.76,2677],["R,PAVITHRA",385937.84,6117],["GU,RICHARD",384698.44,7482],["ERIKSSON,PERNILLA",374934.74,1746],["LOPEZ RODRIGUEZ,ALEJANDRA",366972.45,4468],["MENDOZA PINON,EVER",365519.49,1396],["JAMES HASSLER",347069.13,3170],["KENNEDY, STEVEN",346301.05,41583],["ANITA KIMBRELL",344951.89,3590],["STEVE HINCHLIFFE",344519,7945],["IBARRA MARQUEZ,RAMON",339215.77,204],["YALAMAKUR,RAGHUNATH",339185.2,1810],["DONNA BOYD",327498.25,2770],["LONG, STACEY",320345.49,8271],["OUELLETTE,BRIAN",314774.69,1778],["SILVA,FELIPE",301730.17,767],["VALADES MORENO,JOSE JORGE",297607.09,2423],["MONTES, GUILLERMINA",293099.83,15810],["KUJAWA,KAMILA",288939.12,3500],["STREIT, NICHOLAS",288745.98,14189],["SCOTT GROSSINGER",276660.42,3390],["LARA PEREZ,DANIEL ALBERTO",257706.04,18930],["VELAZQUEZ AGUIRRE,JOSE ISRAEL",254117.69,4245],["ALEJANDRO GARGALLO",253627.18,88980],["JOSE MANUEL VIRUES",249416.39,21330],["SHANNON GREENE",246980.82,11980],["KOLIS, TIM",241099.28,2594],["HERNANDEZ,GEMA",233537.91,306],["TRENT GARBER",230546.05,10585],["OUDSHOORN,MARK",225298.91,1371],["SUE KOELLER",204001.34,7866],["ZHANG,SELINA",201988.14,808],["CRUZ-ALVARADO, EDER",199268.21,2685],["SCHUPP, WILLIAM",198111.16,14722],["SANDRA FERGUSON",194571.62,56562],["PANIAGUA VIDEGARAY,AUGUSTO CESAR",190779.08,3274],["SZWEJK,JAMI",190446.67,3762],["HARMEYER, NICK",186658.51,12200],["KASSANDRA ZURCHER",185750,1830],["LASORSA SALCEDO,NICOLA JOSE",185199.13,1551],["RANDY AMUNDSON",182040.53,2490],["VERELLEN, DAWN",179820,204],["CANELAS,AMANDA",179539.59,2549],["MAIORANO, CHRISTOPHER",178286.95,19105],["MARKPHAN,JIRAMET",157259.01,1326],["DANDE,PRASHANT",156654.12,3603],["ROBERT PETERSON",154777.4,15315],["BONANCIO,AMANDA",154144.87,719],["GARCIA DE LA O,LUIS ANGEL",151892.9,561],["MELVIN, AMELIA",151048.9,5690],["PEREZ, JUAN",144131.3,4925],["LARSON, MICHAEL",141473.27,74868],["MYERS, DEREK",141035.67,10830],["PALOMA GRAU",139843.46,6165],["OSCAR AGUILAR",138741.35,5020],["PENNELL, PAUL",136486.96,6175],["SIMPSON,ROBERT",133250,1038],["ROSE, JOSEPH",132951,17870],["MORENO,MARK",132665.36,204],["CAITLIN CANADA",129351.31,17195],["EASH, ANDY",129158.84,96392],["POULARD,GEOFFREY",128975.92,651],["CULLIFER,JEAN",123628.48,1683],["ROBERTO ANDRADE",120503.88,24390],["JEREMY YODER",119857.86,7520],["KINEL, ROBERT",118913.14,42853],["SMITH STACY R.",116865.78,7740],["CINDY LU",116499.6,6495],["OUELLETTE, BRIAN",114899.93,6396],["MORALES TELLEZ,RICARDO",109416.32,1709],["STACHULSKI, THOMAS",108530.32,39444],["MIKE WATKINS",106142.7,2860],["MACDONALD,SCOTT",105192.79,3366],["FRANCISCO PILES",101901.24,5775],["CHRISMAN DON L.",95818.33,1270],["RODRIGO ROMERO",93449.37,55425],["ANDREW SCOTT",92227.81,5690],["GOMEZ,RAUL",91466.74,11994],["KENDRA MCCLURE",90296.53,2460],["KELLY DUCKETT",89562.37,6600],["BROGDON, THOMAS",87099.32,5525],["SMITH, DAN",82099,23052],["EVA ESTEVE",75722.73,24645],["TREJO,LUCIANO",72906.74,4071],["KATHY PACK",72852,3495],["PASCUAL OLLETA",66670.96,11520],["WOJIHOSKI, JEROME",63416.2,675],["NORTH, ANDREW",62382.25,2040],["AMBER DAI",62036.74,5775],["ROBERT WEIX",61727.06,480],["PACO RIBERA",61385.99,1425],["ANITA BRYANT",59822.42,9135],["INMA PASCUAL",59636.17,525],["JULIO ABAD",58247.01,14700],["COTTER, DAN",57735.02,987],["ZUNIGA,JOSE ALFREDO",57687.41,2826],["BEACHEM, STEVE",57388,390],["KONKOLY,MARLENE",56756.6,6933],["PACO SALIDO",56617.54,8190],["MOTE, TUSHAR",56610.25,870],["RHODES, JEFFREY",56025,45],["RAMIREZ,OLAF ROGELIO",55330.81,1569],["MARKWORT,ERIK",51298.14,1533],["ARMSTRONG, MICHAEL",50950,45],["CARVALHO,SUELEN",49311.72,5480],["AMANDA MENEGHINI",44167.81,2730],["PEREGRINA,EVA MARIA",43206.42,2703],["METALDYNE",42822.39,250],["JACKI RADOSTA",42622.71,1487],["KAVITAKE,PRAKASH",41604.15,210],["GAO,FRANK",40712.19,357],["VILLA, YESENIA",40652.78,1590],["张弩",40295.4,750],["JOSE APARICIO",39484.49,6285],["ROSE, ROBERT",39203.44,2652],["ANGUIANO,FERNANDO IVAN",36827.34,2775],["POTIER,EVANDRO",34630.3,41],["WARNER, MATTHEW",34452.79,255],["BRUINSMA, JERROLD",32900.26,985],["JOAN PEREZ (CALIDAD)",32782.24,7575],["MEDRANO,CESAR EDUARDO",31644.36,5949],["SANTIAGO, JOSE",30987.69,1505],["SAWVEL, CHRISTOPHER",30690.2,1989],["CRAFT,JOSHUA",30500,255],["HOMERO GALLEGOS",30425.56,1415],["LOPATKA, KENNETH",30149.1,520],["STEVENS,MELISSA",29285.8,339],["CICILIAN, BRIAN",29073.56,1560],["GAVIN BURSTALL",29000.6,990],["ZAYAC,JAMES",26852.03,4089],["MORRISH, ROBERT",26733,1890],["HILDEBRANDT, CHAD",26633.22,795],["ÁÉÃÂ?¶‰ºÜ",26209.5,2565],["TRYON, SHAWN",25763,1326],["ARREGUIN,AMELIA JIMENA",24714.37,1020],["JOSE BRAVO",23527.82,5025],["PACO BARTUAL",22278.25,5775],["SOTO NIETO,JORGE PABLO",22191.9,102],["DAVE REINKE",22119.29,1571],["JOSE ANTONIO DIEGO",20932.73,720],["SILVIA BARRIOS",20470.65,10845],["MORENO RODRIGUEZ,RODOLFO",20458,153],["‰?ÅËÈ?",20125.27,4050],["PRANGE, JEFFREY",19781.34,1040],["ALLEN, STEVE",19517.69,4596],["MCGREGOR,WILLIAM",19486.54,711],["FRAPPIER, JOE",18307.98,510],["COTTON, JOSEPH",17535.93,4230],["KOZAK, GREGORY",17257.66,1125],["VICENTE PAU",16992.9,6000],["JUAN MANUEL JAIMES",16146.47,405],["ARAIZA,SAMUEL",15532.52,789],["BORIOLO,DIEGO",15229.36,2078],["NOT ASSIGNED",15228.39,1610],["LAWRENCE,LESINSKI",14878.44,60],["FRAKES,JOHN",14476.56,546],["MELTON,VERCY",13107.9,383],["SZALEWICZ, KEVIN",11957,51],["HUCUL,KYLE",11615.99,694],["BROWNLOW, MONICA",11516.12,1335],["BLAIR,KIMBERLY",11080,153],["PALAZZOLO,RENEE",9795,408],["GARCIA CONTRERAS,ISABEL",9679.46,667],["CHOUDHARI,RAJESH",9082.85,81],["HENDRICKS, ROBERT",8947.73,345],["LIDIA LOPEZ",8802.49,1950],["JUDY SCHLAF",8653.03,180],["BARDELLI, DINO",8241,585],["LITKE, EDWARD",7939.85,975],["COSTELLO,SCOTT",7800,51],["BENENATI, TRACEY",7691.67,264],["PURCHASING DEPARTMENT",7437.15,285],["MEXICO",7388.48,555],["JOE HEADLEY",7371.98,335],["GORANG, AARON",6858.07,2142],["SALDIVAR, JOSE",6856.5,900],["HILL, EDWIN",6678.4,102],["JAVI APARICI",6620.15,2520],["CRISTINA GUILLOT",6399.35,3000],["GRIFFIN, TARA",6349.2,104],["LUEDKE, MATTHEW",6237,210],["CASTILLO, PATRICIA M.",6182.5,255],["QUOTING",6129.93,230],["JAVIER RODRIGUEZ",5897.07,5325],["LORETO SANTAMA",5646.55,3675],["MIRAMONTES, JORGE",5551.5,90],["HOOKER, COREY",4800,51],["LAUREN DOLES",4350,90],["DAVID KROLL",4144.29,495],["SEAN VANALSTINE",3975.49,1390],["KOBER, ARNOLD",3606.36,300],["HLADISH, ED",3564,51],["MAKSIMOVSKI,BORCE",3521.8,None],["GUANDIQUE, CHRISTIAN",2986,1020],["LEMISH, TIMOTHY",2852,1224],["SNELLENBERGER KATHLEEN",2736.8,60],["DIGRAZIA, THOMAS",2687.5,360],["ÈÔÀËÂ?",2575.05,1545],["OSTERLAND,MICHAEL",2568.75,180],["KLEBER, MATTHEW",2417,90],["CRISTINA NOVILLO",2284.53,1890],["PLATZER, JOHN",2064,60],["BOWEN, KALEN",1767.74,2550],["ÈÉ?ÊÎÄ",1729.75,2100],["COSTER, JOHN",1620.8,51],["BOHACEK, ROBERT",1585.86,90],["BEARD, JACOB",1520,510],["SCHINS,MARC",1501.02,102],["GLUECKERT, DAVID",1490,45],["OEZKAYA,OKTAY",1447.54,360],["FERBER, CRAIG",1440,26],["郭攀",1042.54,300],["DAVIS, EISHUN",1028,135],["SUE GONZALES",1000,30],["ANDY KAUN",956.87,120],["PACO MARTINEZ LATORRE",609.43,750],["陈艳",575.37,225],["PAN GUO",520.94,300],["SZYBOWICZ,PATRICK",472.85,60],["BONANNO,FATMEH",456,51],["BOCTOR, ALBAIR",452.4,30],["IMLAY, MICHELLE",410,30],["COMBER, THOMAS",386.86,105],["SHUFF, RANDALL",304,153],["JOEY PINTADO",297.96,60],["KARLSSON,MARIE",215.24,210],["TOMMY DELAY",98.36,60],["LOPEZ,ALEJANDRA",54.35,51],["GAMALIEL MARTINEZ",4.96,195],["WOODWARD GAIL",0,55],["CHURCHILL, MICHAEL",0,52],["CALAHORRANO, HECTOR",0,0],["CANDY UHL - MLS BUYER CODE",-978.13,114700]]
    metaScatter = [{"colIndex":0,"colName":"buyer","colType":"Varchar","unit":None,"type":"aD"},{"colIndex":1,"colName":"SUM OF SPEND AMOUNT","colType":"Float","unit":"$","type":"aM"},{"colIndex":2,"colName":"SUM OF AVERAGE DAY TO PAY","colType":"Float","unit":"$","type":"aM"}]

    result = pd.DataFrame(data=resultScatter)
    # print(result)
    c = CreateChart()
    d = c.dataType(metaScatter)
    print(c.scatter_chart(result, d))
    # print(c.bar_chart(result, d))