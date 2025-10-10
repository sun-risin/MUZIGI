import { useNavigate } from 'react-router-dom';
import "./Login.css";

function Login() { 
  const navigate = useNavigate();

  // 로그인 버튼 클릭 시 실행될 함수
  const handleLogin = () => {
    // 실제로는 아이디/비밀번호 검사 후 성공했을 때 실행됨
    console.log("로그인 성공! 챗 페이지로 이동합니다.");
    // navigate('이동할 주소')를 실행해서 페이지 이동
    navigate('/chat'); 
  };

  // 회원가입 버튼 클릭 시 실행될 함수
  const handleShowSignUp = () => {
    navigate('/signup'); // '/signup' 주소로 이동
  };

  return (
    <div className="login">
      <h2 className="login-title">로그인</h2>
      <input type="text" placeholder="아이디를 입력해주세요" />
      <input type="password" placeholder="비밀번호를 입력해주세요" />
      <button className="login-button" onClick={handleLogin}>로그인</button>
      <button className="link-button" onClick={handleShowSignUp}>회원가입</button>
    </div>
  );
}

export default Login;