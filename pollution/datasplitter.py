import pandas as pd
data="TVM-airpollution (1) (1).xlsx"
f1=pd.read_excel(data)
z=pd.DataFrame(f1)
print(z.head())
print(z[' Date'])
day=[]
month=[]
year=[]
hour=[]
for i in range(len(z[' Date'])):
    day.append(z[' Date'][i][0:2])
    month.append(z[' Date'][i][3:5])
    year.append(z[' Date'][i][6:10])


cons={'year':year,'month':month,'day':day}
f=pd.DataFrame(cons,columns=['year','month','day'])
print(f)
f.to_csv("tvmdata.csv")




