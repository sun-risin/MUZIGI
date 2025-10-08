import "./Login.css";

function Login({ onLogin }) {
return ( 
  <div className="login"> 
    <div className="login-box"> 
        <h2 className="login-title">로그인</h2> 
        <input type="text" placeholder="아이디를 입력해주세요" className="login-input"/> 
        <input type="password" placeholder="비밀번호를 입력해주세요" className="login-input"/> 
        <button className="login-button" onClick={onLogin}>로그인 </button> 
        <p className="signup-text">회원가입</p> </div> </div>
);
}

export default Login;
