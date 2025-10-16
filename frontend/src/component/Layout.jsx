import { Outlet } from 'react-router-dom';
import Logo from '../assets/Logo.png';
import './Layout.css';

const Layout = () => {
  return (
    <div className='layout-container'>
      <header className='app-header'>
        <img src={Logo} alt="로고" className='logo-image' />
      </header>
      <main className='main-content'>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;