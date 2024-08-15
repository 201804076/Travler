import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/navbar.css';

function Navbar() {
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/');
    window.location.reload();
  };

  return (
    <nav>
      <div className="logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>Traveler</div>
      <ul className="menu">
        {/* <li><Link to="#">Home</Link></li> */}
      </ul>
    </nav>
  );
}

export default Navbar;
