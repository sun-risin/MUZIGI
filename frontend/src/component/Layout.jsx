import { Outlet } from 'react-router-dom';
import Logo from '../assets/Logo.png';
import './Layout.css';

const Layout = () => {
  return (
    <div>
      <header style={{ padding: '10px 20px'}}>
        <img src={Logo} alt="로고" style={{ height: '40px' }} />
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;