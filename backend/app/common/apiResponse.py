# 응답 포맷 관련 파일

from flask import jsonify
from typing import Any

class ApiResponse:
    
    # 성공
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
        
    # 실패
    @staticmethod
    def error(
        status: int,
        message: str = "실패", code: str = "000_UNKNOWN_ERR"):
        
        return jsonify({
            "success" : False,
            "code" : code,
            "message" : message,
            "data" : None,
        }), status