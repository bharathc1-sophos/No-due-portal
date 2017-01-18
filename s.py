from flask import request ,render_template,Flask,session,redirect,url_for,jsonify
import MySQLdb

app=Flask(__name__)
db = MySQLdb.connect(host="localhost", user="root", passwd="bharath1997", db="project")
cur = db.cursor()
#cur.execute("SELECT * FROM bharath")
global role
role="0"
@app.route('/')
def log():
	if role=="1":
		if 'username' in session:
			cur.execute("SELECT * FROM phase1 WHERE webmail=%s",[session['username']])
			row=cur.fetchone()
			if row is None:
				cur.execute("SELECT name,rollnum,webmail,programme,dept FROM students WHERE webmail = %s;", [session['username']])
				row=cur.fetchone()
				return render_template("head.html",asa=row)
			else:
				cur.execute("SELECT * FROM phase1 WHERE webmail = %s;", [session['username']])	
				phase1=cur.fetchone()
				cur.execute("SELECT * FROM phase2 WHERE webmail = %s;", [session['username']])
				phase2=cur.fetchone()
				cur.execute("SELECT * FROM phase3 WHERE webmail = %s;", [session['username']])
				phase3=cur.fetchone()
				cur.execute("SELECT * FROM dept WHERE webmail = %s;", [session['username']])
				dept=cur.fetchone()
				cur.execute("SELECT * FROM pre WHERE webmail = %s;", [session['username']])
				pre=cur.fetchone()
				return render_template("student.html",phase1=phase1,phase2=phase2,dept=dept,phase3=phase3,pre=pre)	
	if role=="2":
		if 'username' in session:
			cur.execute("SELECT name,webmail,job,phase FROM admin WHERE webmail = %s;", [session['username']])
			row=cur.fetchone()
			cur.execute('SELECT %s.%s,students.* FROM %s,students WHERE %s.webmail=students.webmail AND %s.%s<>"%s";'%(row[3],row[2],row[3],row[3],row[3],row[2],'not reached'))
			rows=cur.fetchall()
			return render_template("library_home.html",asa=row,rows=rows)				
	return render_template("login.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        session['username']  = request.form['username']
        password_form  = request.form['password']
        global role
        role = request.form['role']
        if role=="1" :
        	cur.execute("SELECT COUNT(1) FROM students WHERE webmail = %s;",[session['username']]) # CHECKS IF USERNAME EXSIST
        	if cur.fetchone()[0]:
            	 cur.execute("SELECT password FROM students WHERE webmail = %s;", [session['username']]) # FETCH THE HASHED PASSWORD
            	for row in cur.fetchall():
 					if password_form == row[0]:
 						return redirect(url_for('log'))
 					else:
 						return render_template("login.html")				
        if role=="2" :
        	cur.execute("SELECT COUNT(1) FROM admin WHERE webmail = %s;",[session['username']]) # CHECKS IF USERNAME EXSIST
        	if cur.fetchone()[0]:
            	 cur.execute("SELECT password FROM admin WHERE webmail = %s;", [session['username']]) # FETCH THE HASHED PASSWORD
            	for row in cur.fetchall():
 					if password_form == row[0]:
 						return redirect(url_for('log'))
 					else:
 						return render_template("login.html")	
           # error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    session.pop('username',None)
    return redirect(url_for('log'))
   
@app.route('/login/submit',methods=['POST','GET'])
def submit():
	error=None
	if 'username' in session:
		if request.method == 'POST':
			cur.execute("INSERT INTO phase1 VALUES (%s,%s,%s,%s,%s);",([session['username']],'pending','pending','accepted','accepted'))
			db.commit()
			cur.execute("INSERT INTO phase2 VALUES (%s,%s,%s,%s,%s);",([session['username']],'not reached','not reached','pending','pending'))	
			db.commit()
			cur.execute("INSERT INTO phase3 VALUES (%s,%s,%s,%s);",([session['username']],'not reached','not reached','not reached'))
			db.commit()
			cur.execute("INSERT INTO dept VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",([session['username']],'pending','pending','pending','pending','pending','pending','pending','pending'))
			db.commit()
			return redirect(url_for('log'))	
	else:
		return redirect(url_for('log'))		

@app.route('/logout')
def logout():
	session.pop('username',None)
	return redirect(url_for('log'))
	
@app.route('/update')
def update():
	if 'username' in session:
		user=request.args.get('status',0,type=str)
		cur.execute("SELECT name,webmail,job,phase FROM admin WHERE webmail = %s;", [session['username']])
		row=cur.fetchone()
		c="accepted"
		cur.execute('UPDATE %s SET %s="%s" WHERE webmail="%s";'%(row[3],row[2],c,user))
		db.commit()
		if row[3]=="phase1" and row[2]=="caretaker":
			cur.execute('UPDATE phase2 SET %s="%s" WHERE webmail="%s";'%('warden','pending',user))	
			db.commit()
		if row[3]=="phase1" and row[2]=="gymkhana":
			cur.execute('UPDATE phase2 SET %s="%s" WHERE webmail="%s";'%('gymkhana','accepted',user))	
			db.commit()	
		if row[3]=="phase2" and row[2]=="warden":
			cur.execute('UPDATE phase3 SET %s="%s" WHERE webmail="%s";'%('registrar','pending',user))
			db.commit()
		if row[2]=="library" or row[2]=="cc":
			cur.execute('SELECT library,cc FROM %s WHERE webmail = "%s";'%(row[3],user))
			temp=cur.fetchone()
			if temp[0]=="accepted" and temp[1]=="accepted":
				cur.execute('UPDATE phase3 SET cclb="accepted" WHERE webmail = "%s";'%(user))
				db.commit()	
		cur.execute('SELECT * FROM %s WHERE webmail = "%s";'%(row[3],user))
		rows=cur.fetchall()
		#for t in rows[0]:
		#	if t=="accepted" or t==user:
		#		s="accepted"
		#	else:
				#if row[3]=="phase1" and row[2]=="caretaker":
				#	cur.execute('UPDATE phase2 SET %s="%s" WHERE webmail="%s";'%('warden',t,user))	
				#	db.commit()
		#		return jsonify(result="asdffj")
				
		if row[3]=="dept":
			cur.execute('SELECT * FROM %s WHERE webmail = "%s";'%(row[3],user))	
			rows=cur.fetchall()
			for t in rows[0]:
				if t=="accepted" or t==user:
					t="acc"
				else:
					return jsonify(result="asdfj")
			cur.execute('UPDATE phase3 SET dept="%s" WHERE webmail="%s";'%('accepted',user))
			db.commit()
		cur.execute('SELECT * FROM %s WHERE webmail = "%s";'%(row[3],user))
		rows=cur.fetchall()
		for t in rows[0]:
			if t=="accepted" or t==user:
				t="acc"
			else:
				return jsonify(result="asdfj")
		cur.execute("INSERT INTO pre VALUES (%s,%s,%s);",([user],'pending','pending',))
		db.commit()					
		#if row[3]=="phase1":
		#	cur.execute('UPDATE phase2 SET %s="%s" WHERE webmail="%s";'%('warden','pending',user))	
		#	db.commit()
		return jsonify(result="asdffj")		
			
	return jsonify(result="asdffj")

@app.route('/lists')
def list():
	if 'username' in session:
		if role=="2":
			return render_template("lib_del.html")
			
	return redirect(url_for('log'))		
			
			
			
			
			
			
			
			
			
			
				
app.secret_key='A0Zr98j/3yX R~XHH!jmN]LWX/,RT'			
