#!/usr/bin/env python3
"""
权限测试脚本
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/auth/login"
DEBUG_URL = f"{BASE_URL}/v1/debug/permission-status"

def test_permission():
    """测试权限"""
    print("开始权限测试...")
    
    # 1. 登录获取token
    login_data = {
        "user_name": "admin",
        "password": "admin123",
        "enterprise_code": "YX-ZNT"
    }
    
    print(f"登录数据: {login_data}")
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"登录响应状态: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("access_token")
            print(f"获取到token: {token[:50]}...")
            
            # 2. 测试权限状态
            headers = {"Authorization": f"Bearer {token}"}
            debug_response = requests.get(DEBUG_URL, headers=headers)
            print(f"权限状态响应: {debug_response.status_code}")
            
            if debug_response.status_code == 200:
                debug_result = debug_response.json()
                print("权限状态:")
                print(json.dumps(debug_result, indent=2, ensure_ascii=False))
            else:
                print(f"权限状态请求失败: {debug_response.text}")
        else:
            print(f"登录失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_permission() 