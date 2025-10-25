import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Mail, Edit, Eye, TestTube } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: Mail },
    { path: '/editor', label: 'Editor', icon: Edit },
    { path: '/testing', label: 'Testing', icon: TestTube },
  ];

  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <Mail className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">
                Template Engine
              </span>
            </Link>
            
            <div className="flex space-x-4">
              {navItems.map(({ path, label, icon: Icon }) => (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === path
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{label}</span>
                </Link>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              Template Engine v1.0
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
