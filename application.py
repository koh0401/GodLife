from flask import Flask, render_template, request, redirect, url_for, session
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.utils import secure_filename
import sys
import sqlite3
import os
import database
import random
import time 
import schedule

application = Flask(__name__)
application.secret_key = "a_long_and_secure_secret_key_12345"

DB_FILE = "users.db"  # db 파일 이름

def initialize_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_status (
            user_id TEXT PRIMARY KEY,
            job TEXT DEFAULT '심각한 백수',
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            last_reset DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan_status (
            user_id TEXT,
            plan_name TEXT,
            complete BOOLEAN,
            content TEXT,
            photo_path TEXT,
            PRIMARY KEY (user_id, plan_name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan_status2 (
            user_id TEXT,
            plan_name TEXT,
            complete BOOLEAN,
            content TEXT,
            photo_path TEXT,
            PRIMARY KEY (user_id, plan_name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan_list (
            user_id TEXT,
            plan_name TEXT,
            PRIMARY KEY (user_id, plan_name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan_status3 (
        user_id TEXT,
        plan_name TEXT,
        complete BOOLEAN,
        content TEXT,
        photo_path TEXT,
        PRIMARY KEY (user_id, plan_name),
        FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        conn.commit()
        
def clear_table():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM plan_status")
        cursor.execute("DELETE FROM plan_status2")
        cursor.execute("DELETE FROM plan_status3")
        cursor.execute("DELETE FROM plan_list")
        conn.commit()
        conn.close()
        print("plan_status와 plan_list 데이터가 삭제되었습니다.")
    except Exception as e:
        print(f"데이터베이스 작업 중 오류 발생: {e}")

# 폴더 내 파일 삭제 함수 (기존 코드 그대로)
def clear_folder(folder_path):
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"{folder_path} 폴더의 모든 파일이 삭제되었습니다.")
    except Exception as e:
        print(f"{folder_path} 폴더 파일 삭제 중 오류 발생: {e}")

# 전체 삭제 작업 함수 (기존 코드 그대로)
def clear_all():
    print("삭제 작업 시작...")
    clear_table()
    clear_folder("./static/img")
    clear_folder("./static/img2")
    print("삭제 작업 완료.")

# 스케줄러 설정 (매일 15:00에 실행)
def schedule_tasks():
    scheduler = BackgroundScheduler()
    scheduler.add_job(clear_all, 'interval', hours=24, start_date='2025-01-14 15:00:00')
    scheduler.start()
    print("스케줄러가 실행 중입니다...")

initialize_db()
schedule_tasks()

@application.route("/")
def hello():
    if "userID" in session: #userID는 session의 키로 존재함. 따로 변수설정 필요없다.
        return render_template("hello.html", username = session.get("userID"), login = True)
    else:
        return render_template("hello.html", login = False)

@application.route("/signup", methods= ["GET", "POST"])#/signup페이지를 방문할 때는 즉, sinup.html을 로드할 때는 GET 요청으로 페이지가 뜬다. 폼이 제출되면 POST요청으로 처리되어서 데이터베이스에 정보를 저장하고 그 뒤에 로직이 실행된다.
def signup():
    if request.method == "POST":#HTTP요청의 메서드를 확인한다.
        _id_ = request.form.get("newId")
        _password_ = request.form.get("newPw")
        print(f"Signup attempt with ID: {_id_}, Password: {_password_}")
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
        
            cursor.execute("SELECT * FROM users WHERE id = ? AND password = ?", (_id_, _password_))#exexute메서드는 튜블로 매개변수를 받는다._id_와 같은 id인 데이터를 찾는다.
            existing_user = cursor.fetchone()#그 행을 출력한다.
            print(f"Database query result: {existing_user}")
            
            cursor.execute("SELECT password FROM users WHERE id = ?", (_id_,))
            stored_password = cursor.fetchone()
            print(f"Stored password: {stored_password}, Entered password: {_password_}")
            
            if existing_user:
                return render_template("signup.html", error = "이미 존재하는 ID와 PASSWORD입니다.")
        
            cursor.execute("INSERT INTO users (id, password) VALUES (?, ?)", (_id_, _password_))#users 테이블에 새로운 사용자를 추가한다.
            cursor.execute("INSERT INTO user_status (user_id) VALUES (?)", (_id_,))
            conn.commit()
        return redirect(url_for("hello"))

    return render_template("signup.html")

@application.route("/login", methods= ["POST"])
def login():
    _id_ = request.form.get("loginId")
    _password_ = request.form.get("loginPw")
    print(f"Login attempt with ID: {_id_}, Password: {_password_}")
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ? AND password = ?", (_id_, _password_))
        user = cursor.fetchone()
        print(f"Database query result: {user}")
        
        cursor.execute("SELECT password FROM users WHERE id = ?", (_id_,))
        stored_password = cursor.fetchone()
        print(f"Stored password: {stored_password}, Entered password: {_password_}")
        
        if user:
            session["userID"] = _id_
            print(f"Session userID set to: {session['userID']}")
            
            cursor.execute("SELECT job, level, experience FROM user_status WHERE user_id = ?", (_id_,))
            status = cursor.fetchone()#fetchone은 첫 번째 행만 반환한다. #튜플 형태임.
            print(status)
            session["job"], session["level"], session["experience"] = status

            cursor.execute("SELECT plan_name FROM plan_list WHERE user_id = ?", (_id_,))
            results = cursor.fetchall()
            plan_list = [row[0] for row in results]
            session["plan_list"] = plan_list

            return redirect(url_for("hello"))

        else:
            print("Login failed: Invalid credentials")
            return render_template("hello.html", error = "존재하지 않은 ID와 PASSWORD입니다.")

@application.route("/logout")
def logout():
    user_id = session["userID"]

    if user_id:#업데이트 해줘야된다.
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE user_status
            SET job = ?, level = ?, experience = ?
            WHERE user_id = ?
            """, (session["job"], session["level"], session["experience"], user_id))
            conn.commit()

    session.clear()

    return redirect(url_for("hello"))

###########################################################################################
@application.route("/home")
def home():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()

        # user_status를 가져옵니다.
        cursor.execute("SELECT * FROM user_status WHERE user_id = ?", (user_id,))
        user_status = cursor.fetchone()  # user_status는 튜플 형태로 반환됩니다.

    # 경험치와 레벨 업데이트
    if session["experience"] == 100:
        session["experience"] = 0
        session["level"] += 1

    if 10 <= session["level"] < 20:
        session["job"] = "건강한 백수"
    elif 20 <= session["level"] < 30:
        session["job"] = "평범한 일상인"
    elif 30 <= session["level"] < 50:
        session["job"] = "성실한 일상인"
    elif 50 <= session["level"]:
        session["job"] = "갓생인"

    return render_template("home.html", job=session["job"], level=session["level"], experience=session["experience"], greeting=personalized_greeting, user_data=user_data)

@application.route("/list1")
def list1():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()

    if session["job"] == "심각한 백수":
        program_list = ["아침 햇볕 받기",
                        "방 청소하기",
                        "가벼운 칼럼 읽기",
                        "새로운 일기장 시작하기",
                        "가벼운 스트레칭하기",
                        "과일 섭취하기",
                        "좋아하는 노래 한 곡 듣기",
                        "10분 산책하기",
                        "아침에 5분 명상하기",
                        "난 훌륭해 10회 복창하기",
                        "5분 거울 앞에서 웃기",
                        "낮잠 20분 자기",
                        "SNS 사용 30분 줄이기",
                        "주간 체크리스트 만들기",
                        "긍정적인 말 하기",
                        "동네 한 바퀴 돌기",
                        "새로운거 배워보기",
                        "10분 스트레칭",
                        "자기 전 감사한 일 3가지 적기",
                        "일어나 창문 열어 환기하기"]

    if session["job"] == "건강한 백수":
        program_list = ["10분 책 읽기",
                        "자전거 타기(못타면 연습하기)",
                        "커피 대신 차 마시기",
                        "도서관에서 책 대출하기",
                        "새로운 취미 시작하기 (예: 퍼즐 맞추기)",
                        "10분간 뉴스 읽기",
                        "사람들과 대화하고 긍정적인 말하기",
                        "주간 체크리스트 짜고 실천하기",
                        "알람 소리 바꿔보기",
                        "친구에게 작은 선물 보내기",
                        "새로운 단어 배워보기",
                        "아침 8시에 일어나기",
                        "1분간 꽃이나 식물 바라보기",
                        "친구와 영화 보기",
                        "저녁에 카페에서 여유 즐기기",
                        "필요없는 것들 정리하기",
                        "30분 운동하기",
                        "하루에 20분 명상하기",
                        "간단한 일기 쓰기",
                        "더 많이 웃기"]

    if session["job"] == "평범한 일상인":
        program_list = ["하루 1시간 운동 루틴 만들기",
                        "아침 30분 독서하기",
                        "새로운 것을 배우기",
                        "새로운 사람과 대화하기",
                        "월간 목표 계획 세우기(주간 목표 달성 후)",
                        "열 가지 감사한 일 적기",
                        "체중 목표 세우고 건강 관리하기",
                        "새로운 취미 시도하기",
                        "새로운 운동 시작하기(예: 수영 등)",
                        "외출해서 자연을 만끽하기",
                        "도전적인 운동하기",
                        "주간 계획에서 한 가지 새로운 활동 추가하기",
                        "책 1시간 읽기",
                        "45분 운동하기",
                        "아침 조깅하기",
                        "1시간 자기계발 시간 가지기",
                        "새로운 장소 탐방하기",
                        "30분 집중해서 일하기",
                        "친구와 운동 도전하기",
                        "영화 혹은 노래방등 친구들과 놀기"]

    if session["job"] == "성실한 일상인":
        program_list = ["매일 1시간 이상 운동하기",
                        "개인 프로젝트 시작하기 (책 쓰기 등)",
                        "자신을 위한 기술을 연마하기",
                        "새로운 사람과 네트워킹하기",
                        "월간 예산 설정하고 지키기",
                        "새로운 운동 종목 도전하기 (예: 마라톤)",
                        "개인적인 성장 목표 세우기",
                        "자원봉사 참여하여 사회적 기여하기",
                        "책 1권 완독하기",
                        "일상생활에서 명상과 마음 챙김 실천하기",
                        "새로운 취미에 몰입하기",
                        "프로젝트 리더 역할 맡기",
                        "기부나 자선 활동 참여하기",
                        "혼자 여행 계획 세우기",
                        "독립적인 생활 시작하기 (경제적 독립 등)",
                        "지속 가능한 소비 습관 만들기",
                        "식습관 개선하기",
                        "네트워크 확장 및 사회적 영향력 키우기",
                        "연말까지 목표 달성을 위한 계획 세우기",
                        "자산 관리 및 재테크 공부하기"]
    
    if session["job"] == "갓생인":
        program_list = ["1시간 이상 운동하기",
                        "새로운 직업을 위한 기술 배워보기",
                        "새로운 아이디어 실제로 이행하기",
                        "하루 한 가지 프로젝트 완성하기",
                        "자신의 전문 분야에 기여하기",
                        "정기적으로 투자 시작하기",
                        "한 가지 창의적인 작업 해보기(그림 등)",
                        "인플루언서로 활동해보기",
                        "다이어트 목표 달성을 위한 계획 새우기",
                        "새로운 언어 배워보기",
                        "자신만의 연간 목표 계획 후 실천하기",
                        "자격증 공부 후 취득하기",
                        "돈을 절약해서 해외여행 가기",
                        "타인과 협업하여 프로젝트 성공시키기",
                        "독립적인 수입원 만들기",
                        "강연이나 세미나 진행하기",
                        "자기계발 서적 50권 선정 후 읽기",
                        "커리어 목표 달성하기",
                        "새로운 대규모 프로젝트 주도하기",
                        "지속 가능한 생활방식 완성하기"]
    
    length = len(program_list)
    return render_template("list1.html", program_list = program_list, length = length, greeting = personalized_greeting, user_data = user_data)

@application.route("/give_info")
def give_info():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"
    plan_name = request.args.get("plan")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()

        cursor.execute("SELECT complete, content, photo_path FROM plan_status WHERE user_id = ? AND plan_name = ?",(user_id, plan_name))
        plan_status = cursor.fetchone()

    if plan_status:
        complete, content, photo = plan_status
        check = True
    else:
        complete = False
        content = ""
        photo = None
        check = False

    return render_template("give_info.html", greeting = personalized_greeting, user_data = user_data, plan = plan_name, complete = complete, content = content, photo = photo, check = check)

@application.route("/upload_done2", methods= ["POST"])
def upload_done2():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"

    plan_name = request.form.get("plan")
    complete = request.form.get("complete") is not None
    content = request.form.get("content")
    uploaded_files2 = request.files["file"]

    if complete == None:
        complete = False
    else:
        complete = True

        if session["job"] == "심각한 백수":
            session["experience"] += 50
        elif session["job"] == "건강한 백수":
            session["experience"] += 25
        elif session["job"] == "평범한 일상인":
            session["experience"] += 20
        elif session["job"] == "성실한 일상인":
            session["experience"] += 10
        elif session["job"] == "갓생인":
            session["experience"] += 5

    if uploaded_files2:
        filename2 = secure_filename(uploaded_files2.filename)
        file_extension2 = filename2.split('.')[-1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png']

        if file_extension2 not in allowed_extensions:
            return "파일 형식이 유효하지 않습니다.", 400
        file_path = f"static/img2/{user_id}_{plan_name}.{file_extension2}"
        uploaded_files2.save(file_path)
        photo_path = f"img2/{user_id}_{plan_name}.{file_extension2}"
    else:
        file_path = None
        photo_path = None

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM plan_status WHERE user_id = ? AND plan_name = ?
        """, (user_id, plan_name))
        existing = cursor.fetchone()

        if existing:
        # 데이터가 이미 있으면 업데이트
            cursor.execute("""
            UPDATE plan_status
            SET complete = ?, content = ?, photo_path = ?
            WHERE user_id = ? AND plan_name = ?
            """, (complete, content, photo_path, user_id, plan_name))#photo_path에 photo__path를 받는다.
        else:
        # 데이터가 없으면 삽입
            cursor.execute("""
            INSERT INTO plan_status (user_id, plan_name, complete, content, photo_path)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, plan_name, complete, content, photo_path))

        conn.commit()

    return redirect(url_for("give_info", plan = plan_name))

############################################################################################
@application.route("/list2")
def list3():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"
    
    job = session["job"]
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()

    plan_list = session.get("plan_list", []) #session에 plan_list가 있으면 그 리스트를 가져오고, 없으면 빈 리스트를 반환한다.
    #session = {"plan_list": ["planA", "planB]}
    if plan_list:
        length = len(plan_list)
    else:
        length = 0

    return render_template("list3.html", plan_list = plan_list, length = length, greeting = personalized_greeting, user_data = user_data, job = job)

@application.route("/makePlanlist")
def makePlanlist():
    user_id = session["userID"]
    plan = request.args.get("plan")
    
    if "plan_list" not in session:
        session["plan_list"] = []

    session["plan_list"].append(plan)
    session.modified = True #plan_list에 새로운 plan을 추가했을 때, session을 변경해주기 위해
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO plan_list (user_id, plan_name)
        VALUES (?, ?)
        """, (user_id, plan))
        conn.commit
        
    return redirect(url_for("list3"))

@application.route("/give_info2")
def give_info2():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"
    plan_name = request.args.get("plan")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        cursor.execute("SELECT complete, content, photo_path FROM plan_status2 WHERE user_id = ? AND plan_name = ?",(user_id, plan_name))
        plan_status = cursor.fetchone()
        
    if plan_status:
        complete, content, photo_path = plan_status
        check = True
    else:
        complete = False
        content = ""
        photo_path = None
        check = False

    print(photo_path)
    print(complete)
    print(content)
    print(check)
    return render_template("give_info2.html", greeting = personalized_greeting, user_data = user_data, plan = plan_name, complete = complete, content = content, photo = photo_path, check = check)

@application.route("/upload_done", methods= ["POST"])
def upload_done():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"
    
    plan_name = request.form.get("plan")
    complete = request.form.get("complete") is not None
    content = request.form.get("content")
    uploaded_files = request.files["file"]

    if complete == None:
        complete = False
    else:
        complete = True

        if session["job"] == "심각한 백수":
            session["experience"] += 50
        elif session["job"] == "건강한 백수":
            session["experience"] += 25
        elif session["job"] == "평범한 일상인":
            session["experience"] += 20
        elif session["job"] == "성실한 일상인":
            session["experience"] += 10
        elif session["job"] == "갓생인":
            session["experience"] += 5    

    if uploaded_files:
        filename = secure_filename(uploaded_files.filename)
        file_extension = filename.split('.')[-1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png']

        if file_extension not in allowed_extensions:
            return "파일 형식이 유효하지 않습니다.", 400
        file_path = f"static/img/{user_id}_{plan_name}.{file_extension}"
        uploaded_files.save(file_path)
        photo_path = f"img/{user_id}_{plan_name}.{file_extension}"
    else:
        file_path = None
        photo_path = None

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM plan_status2 WHERE user_id = ? AND plan_name = ?
        """, (user_id, plan_name))
        existing = cursor.fetchone()
        print(existing, 0)

        if not existing:#존재하지 않으면 넣는다.
            cursor.execute("""
            INSERT INTO plan_status2 (user_id, plan_name, complete, content, photo_path)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, plan_name, complete, content, photo_path))#photo_path에 photo__path를 받는다.
        conn.commit()

    return redirect(url_for("give_info2", plan = plan_name))
###################################################################################
@application.route("/list4")
def list4():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()

    special_list = ["부모님께 전화 드리기",
                    "주말에 부모님과 같이 영화 보기",
                    "부모님을 위한 작은 선물 준비하기",
                    "부모님과 함께 식사하기",
                    "부모님께 안부 묻기",
                    "부모님과 산책하기",
                    "부모님께 감사한 마음을 문자 보내기",
                    "부모님과 대화하기",
                    "부모님과 가벼운 운동하기",
                    "부모님에게 작은 칭찬하기",
                    "부모님을 집안일 도와드리기",
                    "부모님과 가벼운 여행 계획하기",
                    "부모님께 편지 쓰기",
                    "부모님께 음악이나 노래 추천하기",
                    "부모님이 음식 해 드리기",
                    "부모님에게 사랑의 표현하기",
                    "부모님과 함께 쇼핑 가기",
                    "부모님에게 꽃다발 선물하기",
                    "부모님이 좋아하는 프로그램 같이 보기",
                    "부모님에게 취미를 소개하기",
                    "부모님과 함께 외출 계획하기",
                    "부모님께 손편지 작성하기",
                    "부모님께 행복한 추억을 만들어 드리기",
                    "부모님이 음식을 같이 만들어보기",
                    "부모님께 사랑한다고 말하기",
                    "부모님을 위해 하루를 특별하게 보내기",
                    "부모님께 아침 인사 드리기",
                    "부모님께 사진 찍어 드리기",
                    "부모님과 함께 가족 게임 하기",
                    "부모님과 함께하는 시간을 갖기",
                    "부모님과 함께 지역 봉사활동 참여하기",
                    "부모님께 책 선물하기",
                    "부모님에게 액세서리 선물하기",
                    "부모님과 함께 산책하며 추억 만들기",
                    "부모님에게 좋은 영화를 추천해 드리기",
                    "부모님을 위해 마음을 담아 요리하기",
                    "부모님과 박물관이나 전시회 가기",
                    "부모님께 커피나 차 가져다 드리기",
                    "부모님의 집안 정리 돕기"]

    length = len(special_list)
    return render_template("list4.html", special_list = special_list, length = length, greeting = personalized_greeting, user_data = user_data)

@application.route("/give_info3")
def give_info3():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"
    plan_name = request.args.get("plan")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()

        cursor.execute("SELECT complete, content, photo_path FROM plan_status3 WHERE user_id = ? AND plan_name = ?",(user_id, plan_name))
        plan_status = cursor.fetchone()

    if plan_status:
        complete, content, photo = plan_status
        check = True
    else:
        complete = False
        content = ""
        photo = None
        check = False

    return render_template("give_info3.html", greeting = personalized_greeting, user_data = user_data, plan = plan_name, complete = complete, content = content, photo = photo, check = check)

@application.route("/upload_done3", methods= ["POST"])
def upload_done3():
    user_id = session["userID"]
    personalized_greeting = f"안녕하세요, {user_id}님!"

    plan_name = request.form.get("plan")
    complete = request.form.get("complete") is not None
    content = request.form.get("content")
    uploaded_files2 = request.files["file"]

    if complete == None:
        complete = False
    else:
        complete = True
        session["level"] += 1

    if uploaded_files2:
        filename2 = secure_filename(uploaded_files2.filename)
        file_extension2 = filename2.split('.')[-1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png']

        if file_extension2 not in allowed_extensions:
            return "파일 형식이 유효하지 않습니다.", 400
        file_path = f"static/img2/{user_id}_{plan_name}.{file_extension2}"
        uploaded_files2.save(file_path)
        photo_path = f"img2/{user_id}_{plan_name}.{file_extension2}"
    else:
        file_path = None
        photo_path = None

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM plan_status WHERE user_id = ? AND plan_name = ?
        """, (user_id, plan_name))
        existing = cursor.fetchone()

        if existing:
        # 데이터가 이미 있으면 업데이트
            cursor.execute("""
            UPDATE plan_status3
            SET complete = ?, content = ?, photo_path = ?
            WHERE user_id = ? AND plan_name = ?
            """, (complete, content, photo_path, user_id, plan_name))#photo_path에 photo__path를 받는다.
        else:
        # 데이터가 없으면 삽입
            cursor.execute("""
            INSERT INTO plan_status3 (user_id, plan_name, complete, content, photo_path)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, plan_name, complete, content, photo_path))

        conn.commit()

    return redirect(url_for("give_info3", plan = plan_name))

if __name__ == "__main__":
    application.run(host='0.0.0.0')
    