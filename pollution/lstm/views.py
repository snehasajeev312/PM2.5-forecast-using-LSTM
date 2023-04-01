from django.shortcuts import render,HttpResponseRedirect
import MySQLdb
db=MySQLdb.connect("localhost","root","","pollution")
c=db.cursor()
# Create your views here.
def index(request):
    return render(request,'index.html')
def ahome(request):
    return render(request,'ahome.html')
def uhome(request):
    return render(request,'uhome.html')

def reg(request):
    msg=""
    if request.POST:
        name=request.POST.get("name")
        email=request.POST.get("email")
        uname=request.POST.get("uname")
        password=request.POST.get("password")
        c.execute("select count(*) from reg where email='"+ email +"' or uname='"+ uname +"' ")
        count=c.fetchone()
        if count[0]>0:
            msg="data already exist try another"
        else:           
            c.execute("insert into reg values('','"+name+"','"+email+"','"+uname+"','"+password+"')")
            msg="registration succesful"
        db.commit()
    
    return render(request,'reg.html',{"msg":msg})

def login(request):
    msg=""
    if request.POST:
        uname=request.POST.get("uname")
        password=request.POST.get("password")
        c.execute("select * from reg where password='"+ password +"' and uname='"+ uname +"' ")
        user=c.fetchone()
        if uname=="admin" and password=="admin":
            request.session["uname"]=uname
            return HttpResponseRedirect("/ahome/")
        elif user:
            request.session["uname"]=uname
            request.session["name"]=user[1]
            return HttpResponseRedirect("/uhome/")
        else:
            msg="Enter valid data"
        
    return render(request,'login.html',{"msg":msg})

def feedback(request):
    c.execute("select * from feedback where (fto='"+ request.session["uname"] +"' and frm='admin') or (fto='admin' and frm='"+ request.session["uname"] +"')")
    data=c.fetchall()
    print(data)
    if request.POST:
        feedback=request.POST.get("feedback")
        import datetime
        date=datetime.date.today()
        fto="admin"
        c.execute("insert into feedback values('','"+ feedback +"','"+ request.session["uname"] +"','"+ fto +"','"+ str(date) +"')")
        db.commit()
        return HttpResponseRedirect("/feedback/")
    return render(request,'feedback.html',{'data':data,"uname":request.session["uname"],"name":request.session["name"]}) 

def vfeedback(request):
    c.execute("select * from feedback where fto='admin' order by fid desc")
    data=c.fetchall()
    return render(request,'vfeedback.html',{"data":data})


def rfeed(request):
    data=""
    if request.GET.get("id"):
        id=request.GET.get("id")
        c.execute("select * from feedback where (fto='"+ id +"' and frm='admin') or (fto='admin' and frm='"+ id +"')")
        data=c.fetchall()

    if request.POST:
        feedback=request.POST.get("feedback")
        import datetime
        date=datetime.date.today()
        frm="admin"
        c.execute("insert into feedback values('','"+ feedback +"','"+ frm +"','"+ request.GET.get("id") +"','"+ str(date) +"')")
        db.commit()
        return HttpResponseRedirect("/rfeed/?id="+request.GET.get("id"))

    return render(request,'rfeed.html',{"data":data})


def predict(request):
    predicted=errors=user=""
    request.session['values']=""

    if request.POST:
        user= request.session["uname"]
        import forecasting
        errors,predicted=forecasting.predict()
        predicted=(predicted*100).tolist()
        predicted=predicted[0:10]
        print(list(errors))
        request.session['values']="value"

       
       
    return render(request,'predict.html',{'prediction':predicted,"errors":errors,"user": user})



def error(request):
   
    return render(request,'error.html')

def graph(request):
    value=request.session['values']
    if value=="":
        msg=""
    else:
        msg="value"
    return render(request,'graph.html',{"msg":msg})

def apredict(request):
    predicted=errors=user=""
    request.session['values']=""
    if request.POST:
        user= request.session["uname"]
        import forecasting
        errors,predicted=forecasting.predict()
        predicted=(predicted*100).tolist()
        predicted=predicted[0:10]
        print(errors)
        request.session['values']="value"
    return render(request,'apredict.html',{'prediction':predicted,"errors":errors,"user": user})


def graph1(request):
    value=request.session['values']
    if value=="":
        msg=""
    else:
        msg="value"
    return render(request,'graph1.html',{"msg":msg})

