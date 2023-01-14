from flask_restful import Resource, fields, marshal_with,reqparse
from flask import jsonify, send_file
from application.validation import BusinessValidationError, NotFoundError
from application.database import db
from application.models import Users, List, Tasks
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from application import tasks
from datetime import datetime
import sqlite3
import pandas as pd
import os
from time import perf_counter_ns




create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument("email")
create_user_parser.add_argument('password')

output_fields = {
    "id":fields.Integer,
    "email":fields.String,
    "name":fields.String
}

class UserAPI(Resource):
    @marshal_with(output_fields)
    @jwt_required()
    def get(self, id):
        if id is None:
            raise NotFoundError(status_code=404)
        user = Users.query.filter_by(id=id).count()
        if user > 0:
            userdata=Users.query.filter_by(id=id).first()
            
        return userdata
        
    # @marshal_with(output_fields)
    def post(self):
        args = create_user_parser.parse_args()
        email = args.get("email",None)
        password = args.get("password",None)
        # if email is None:
        #     raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="Email is required")
        if email is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="email is required")
        if "@" in email:
            pass
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Invalid email")
        user = Users.query.filter_by(email=email, password=password).count()
        token = ""
        if user > 0:
            userdata=Users.query.filter_by(email=email, password=password).first()
            token = create_access_token(identity=userdata.id)
            
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="User Does Not Exist")
        return jsonify({"userdata":userdata,"token":token})

create_new_user_parser = reqparse.RequestParser()
create_new_user_parser.add_argument("name")
create_new_user_parser.add_argument("email")
create_new_user_parser.add_argument('password')

class CreateUserAPI(Resource):
    # @marshal_with(output_fields)
    def post(self):
        args = create_new_user_parser.parse_args()
        name= args.get('name',None)
        email= args.get('email',None)
        password= args.get('password',None)
        user = Users.query.filter_by(email=email).count()
        if user:
            raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="Duplicate user")
        registeruser = Users(name=name, email=email, password=password)
        token = create_access_token(identity=registeruser.id)
        db.session.add(registeruser)
        db.session.commit()
        # return registeruser
        return jsonify({"registeruser":registeruser,"token":token})


# List API -------------------------------------
output_list_fields = {
    "id": fields.Integer,
    "listname":fields.String,
    "userid": fields.Integer  
}
create_list_parser = reqparse.RequestParser()
create_list_parser.add_argument("listName")
create_list_parser.add_argument("listid")
create_list_parser.add_argument("userid")


class ListAPI(Resource):
    # Add List------------------
    @marshal_with(output_list_fields)
    def post(self):
        args = create_list_parser.parse_args()
        userid= args.get('userid', None)
        ListName = args.get('listName', None)
        print("userdaa", userid, ListName)
        addtolist = List(listname=ListName, userid=userid)
        db.session.add(addtolist)
        db.session.commit()
        return addtolist
    # Get List and Data of user-------------
    # ----------------------------------------------------

    @jwt_required()
    def get(self, id):
        start = perf_counter_ns()
        list = List.query.filter_by(userid = id).all()
        tasks = Tasks.query.filter_by(userID = id).all()
        stop = perf_counter_ns()
        print("time taken", stop-start)
        response = {
            "list":list,
            "tasks": tasks,
        }
        return jsonify(response)
    # Delete List---------------
    def delete(self, id):
        deletelist=List.query.filter_by(id=id).first()
        deletetask=Tasks.query.filter_by(parent=id).count()
        if deletetask > 0:
            db.session.query(Tasks).filter_by(parent=id).delete()
        db.session.delete(deletelist)
        db.session.commit()
        return jsonify({"msg": "List Deleted Successfully"})
    # Update List-----------------
    @marshal_with(output_list_fields)
    def put(self, id):
        args = create_list_parser.parse_args()
        listid = args.get('listid')
        editlist=List.query.filter_by(id=listid, userid=id).first()
        editlist.listname = args.get("listName", None)
        db.session.commit()
        return editlist

# -------------------------------Task Content----------------------------
task_parser = reqparse.RequestParser()
task_parser.add_argument('id')
task_parser.add_argument('title')
task_parser.add_argument('content')
task_parser.add_argument('deadline')
task_parser.add_argument('flag')
task_parser.add_argument('parent')
task_parser.add_argument('userID')
output_task_fields = {
    "id": fields.Integer,
    "title":fields.String,
    "content": fields.String,
    "deadline": fields.String,
    "flag": fields.Integer,
    "parent": fields.Integer,
    "userID": fields.Integer
}
class TaskAPI(Resource):
    # Add Task API 
    @marshal_with(output_task_fields)
    def post(self):
        args = task_parser.parse_args()
        title = args.get("title")
        content = args.get("content")
        deadline = args.get("deadline")
        flag = args.get("flag")
        parent = args.get("parent")
        userid= args.get('userID', None)
        # lastUpdate=datetime.now().strftime("%I:%M:%S %p %d-%b-%Y")
        addTaskToList = Tasks(title=title, content=content, deadline=deadline, flag=flag, parent=parent, userID=userid)
        db.session.add(addTaskToList)
        db.session.commit()
        return addTaskToList
    # Delete Task API
    @marshal_with(output_task_fields)
    def delete(self, id):
        taskdelete = Tasks.query.filter_by(id=id).first()
        db.session.delete(taskdelete)
        db.session.commit()
        return taskdelete
    
    # Update Task API
    @marshal_with(output_task_fields)
    def put(self, id):
        args = task_parser.parse_args()
        taskid = args.get('id')
        taskdata = Tasks.query.filter_by(id=taskid).first()
        taskdata.title = args.get("title")
        taskdata.content = args.get("content")
        taskdata.deadline = args.get("deadline")
        taskdata.flag = args.get("flag")
        taskdata.parent = args.get("parent")
        # taskdata.lastUpdate=datetime.now().strftime("%I:%M:%S %p %d-%b-%Y")
        db.session.commit()
        return taskdata

class DownloadTask(Resource):
    def get(self, id):
        con = sqlite3.connect('./database/db.sqlite')
        sql = """select title,content,deadline, lastUpdate, flag as status, parent as belongTo from tasks where parent == """ +id
        # sql = List.query.filter_by(userid=id).all()
        df = pd.read_sql_query(sql, con)
        df.to_csv('./exceldownload/myTasks-'+ id+'.csv')
        return send_file('./exceldownload/myTasks-'+ id+'.csv', as_attachment=True)
        os.remove('./exceldownload/myTasks-'+ id+'.csv')


class DownloadList(Resource):
    def get(self, id):
        con = sqlite3.connect('./database/db.sqlite')
        sql = """select id, listname from list where userid == """+id
        # sql = """select * from list,tasks where list.userid=tasks.userID and list.id= tasks.parent and list.userid="""+id+""" order by list.listname"""
        # sql = List.query.filter_by(userid=id).all()
        df = pd.read_sql_query(sql, con)
        df.to_csv('./exceldownload/myList-'+ id+'.csv')
        return send_file('./exceldownload/myList-'+id+'.csv', as_attachment=True)

class DownloadData(Resource):
    def get(self, id):
        con = sqlite3.connect('./database/db.sqlite')
        sql = """select * from list,tasks where list.userid=tasks.userID and list.id= tasks.parent and list.userid="""+id+""" order by list.listname"""
        df = pd.read_sql_query(sql, con)
        df.to_csv('./exceldownload/myData-'+ id+'.csv')
        return send_file('./exceldownload/myData-'+id+'.csv', as_attachment=True)



        

class StartWorker(Resource):
    def get(self,id):
        print("its running", id)
        job = tasks.print_current_time_job.apply_async(countdown=10)
        result = job.wait()
        return jsonify({"message":"its working", "job":str(result)})




    
        
        