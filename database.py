import pandas as pd
import os

def get_user_data_file(user_id):
    return f"data/{user_id}_data.csv"

def save(user_id, plan, complete, built):
    user_data_file = get_user_data_file(user_id)
    
    if not os.path.exists(user_data_file):
        df = pd.DataFrame(columns = ["index", "plan", "complete", "built"])
    else:
        df = pd.read_csv(user_data_file)
    
    new_idx = len(df)#행의 개수를 나타낸다. column은 포함 안한다.
    new_data = pd.DataFrame({"index":[new_idx], "plan":[plan], "complete":[complete], "built":[built]})
    
    df = pd.concat([df, new_data], ignore_index = True)
    df.to_csv(user_data_file, index = False)
    
    return None

def load_list(user_id):#테이블을 리스트로 바꾸는 함수   
    user_data_file = get_user_data_file(user_id)
    
    if not os.path.exists(user_data_file):
        return []
    
    df = pd.read_csv(user_data_file)#테이블
    
    return df.values.tolist()#df.value는 2차원 배열 df.value.tolist는 배열을 리스트로

def now_index(user_id):
    user_data_file = get_user_data_file(user_id)
    
    if not os.path.exists(user_data_file):
        return 0
    
    df = pd.read_csv(user_data_file)
    
    return len(df)-1

def load_plan(user_id, idx):
    user_data_file = get_user_data_file(user_id)
    
    if not os.path.exists(user_data_file):
        return None
    
    df = pd.read_csv(user_data_file)
    if idx < len(df):
        return df.iloc[idx].to_dict()
    return None

if __name__ =="__main__":
    load_list()