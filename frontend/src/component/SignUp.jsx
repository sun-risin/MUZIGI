import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SignUp.css";

function SignUp() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const navigate = useNavigate();

  const handleSignUp = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId,
          password,
          nickname,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert("회원가입 성공!");
        navigate("/login");
      } else {
        alert(data.message || "회원가입 실패");
      }
    } catch (error) {
      console.error("회원가입 중 오류 발생:", error);
      alert("서버와 연결할 수 없습니다.");
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
      />
      <input
        type="password"
        placeholder="비밀번호를 입력해주세요"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <input
        type="text"
        placeholder="사용할 닉네임을 입력해주세요"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
      />
      <button className="signup-button" onClick={handleSignUp}>
        가입하기
      </button>
    </div>
  );
}

export default SignUp;
