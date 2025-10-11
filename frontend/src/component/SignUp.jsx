import { useNavigate } from 'react-router-dom';
import './SignUp.css'; 

function SignUp() {
  const navigate = useNavigate();

  const handleSignUp = () => {
    alert("회원가입이 완료되었습니다!");
    navigate('/'); // 회원가입 후 로그인 페이지로 이동
  };

  return (
    <div className="signup">
      <h2 className="signup-title">회원가입</h2>
      
      <input type="text" placeholder="아이디를 입력해주세요" />
      <input type="password" placeholder="비밀번호를 입력해주세요" />
      <input type="name" placeholder="사용할 닉네임을 입력해주세요" />

      <button className="signup-button" onClick={handleSignUp}>가입하기</button>
    </div>
  );
}

export default SignUp;