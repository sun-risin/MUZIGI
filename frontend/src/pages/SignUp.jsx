import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SignUp.css";

function SignUp() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [isLoading, setIsLoading] = useState(false); //로딩 상태
  const navigate = useNavigate(); //페이지 이동 함수
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const validateForm = () => { // 따로 확인 한 번 더 실행
    if (!userId) {
      alert("아이디를 입력해주세요.");
      return false;
    }
    if (!password) {
      alert("비밀번호를 입력해주세요.");
      return false;
    }
    if (password.length < 6) {
        alert("비밀번호는 6자 이상이어야 합니다.");
        return false;
    }
    if (!nickname) {
      alert("닉네임을 입력해주세요.");
      return false;
    }
    return true;
  };

  const handleSignUp = async () => {
    if (!validateForm()) return; // 입력값 이상하면 서버 요청 못하게 막아둠

    setIsLoading(true); //ui 상태 변경, 버튼 클릭시 화면 렌더링

    try {
      const response = await fetch("http://localhost:5000/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ userId, password, nickname, }),
      });

      const data = await response.json();

      if (response.ok === 201) {
        alert("회원가입 성공!");
        navigate("/login");
        return;
      }
      if (response.status === 409) {
        alert("이미 존재하는 아이디입니다.");
        return;  
      }
        alert(data?.message || "회원가입 중 문제가 발생했습니다.");
      }
      catch (error) {
      console.error("회원가입 중 오류 발생:", error);
      alert("서버와 연결할 수 없습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signup">
      <h2 className="signup-title">회원가입</h2>
      <input
        type="text"
        placeholder="아이디를 입력해주세요"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        disabled={isLoading}
      />
      <input
        type="password"
        placeholder="비밀번호를 입력해주세요"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        disabled={isLoading}
      />
      <input
        type="text"
        placeholder="사용할 닉네임을 입력해주세요"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
        disabled={isLoading}
      />
      <button
        className="signup-button"
        onClick={handleSignUp}
        disabled={isLoading}
      >
        {isLoading ? "가입 처리 중..." : "가입하기"}
      </button>
    </div>
  );
}

export default SignUp;