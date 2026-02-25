# 응답 포맷 관련 파일

from flask import jsonify
from typing import Any
from backend.app.common.exception.errorCode import ErrorCode  

"""
{
    success - 성공 여부 (T or F)
    code - http status string (custom exception 때문에 str 형식.)
    message - 응답 메시지
    data - 반환 데이터. nullable
},
status - 실제 응답 http status (200, 400, 401...)
"""

class ApiResponse:
    
    # --- 성공
    @staticmethod
    def success(
        status: int,
        message: str = "성공", data: Any = None):
        
        return jsonify({
            "success" : True,
            "code" : str(status),
            "message" : message,
            "data" : data,
        }), status
        
        
    # --- 실패
    # 범용적
    @staticmethod
    def error(status: int, message: str = "실패"):
        
        return jsonify({
            "success" : False,
            "code" : str(status),
            "message" : message,
            "data" : None,
        }), status
        
    # custom exception
    @staticmethod
    def error_byCode(error_code: ErrorCode):
        
        return jsonify({
            "success" : False,
            "code" : error_code.code,
            "message" : error_code.message,
            "data" : None,
        }), error_code.status