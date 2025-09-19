import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const Nav = styled.nav`
  background: #1d2327;
  padding: 0;
  border-bottom: 1px solid #2c3338;
`;

const NavContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 20px;
`;

const Logo = styled.div`
  color: #fff;
  font-size: 20px;
  font-weight: 600;
  padding: 15px 0;
  margin-right: 40px;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 0;
`;

const NavLink = styled(Link)`
  color: #a7aaad;
  text-decoration: none;
  padding: 15px 20px;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
  
  &:hover {
    color: #00a32a;
  }
  
  &.active {
    color: #fff;
    border-bottom-color: #2271b1;
  }
`;

function Navbar() {
  const location = useLocation();

  return (
    <Nav>
      <NavContainer>
        <Logo>Metrics System</Logo>
        <NavLinks>
          <NavLink 
            to="/" 
            className={location.pathname === '/' ? 'active' : ''}
          >
            Dashboard
          </NavLink>
          <NavLink 
            to="/tasks" 
            className={location.pathname === '/tasks' ? 'active' : ''}
          >
            Tasks
          </NavLink>
        </NavLinks>
      </NavContainer>
    </Nav>
  );
}

export default Navbar;
