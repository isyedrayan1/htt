import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Flag, BarChart3, Users, Target, Menu, X } from 'lucide-react';

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', icon: BarChart3, label: 'Driver Analysis' },
    { path: '/coaching', icon: Flag, label: 'Coaching Cards' },
    { path: '/evidence', icon: Users, label: 'Evidence Explorer' },
    { path: '/compare', icon: Target, label: 'Compare Drivers' },
    { path: '/live', icon: Flag, label: 'Live Race Demo' },
  ];

  const isActive = (path) => {
    return location.pathname === path || (path === '/drivers' && location.pathname.startsWith('/drivers'));
  };

  return (
    <nav className="fixed top-0 w-full bg-racing-black/95 backdrop-blur-md border-b border-racing-red/30 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-racing-red rounded-lg flex items-center justify-center">
              <Flag className="w-5 h-5 text-white" />
            </div>
            <span className="text-racing font-bold text-xl text-white">
              AI Driver Coach
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map(({ path, icon: Icon, label }) => (
                <Link
                  key={path}
                  to={path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
                    isActive(path)
                      ? 'bg-racing-red text-white'
                      : 'text-racing-silver hover:text-white hover:bg-racing-gray'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{label}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Status Indicator */}
          <div className="hidden md:flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="status-indicator status-green"></div>
              <span className="text-sm text-racing-silver">Live</span>
            </div>
            <div className="text-sm text-racing-silver">
              COTA
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-racing-silver hover:text-white hover:bg-racing-gray focus:outline-none"
            >
              {isMobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-racing-black/98 border-t border-racing-red/30">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`block px-3 py-2 rounded-md text-base font-medium transition-all duration-200 flex items-center space-x-2 ${
                  isActive(path)
                    ? 'bg-racing-red text-white'
                    : 'text-racing-silver hover:text-white hover:bg-racing-gray'
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Icon className="w-5 h-5" />
                <span>{label}</span>
              </Link>
            ))}
            <div className="flex items-center justify-between px-3 py-2 mt-4 pt-4 border-t border-racing-silver/20">
              <div className="flex items-center space-x-2">
                <div className="status-indicator status-green"></div>
                <span className="text-sm text-racing-silver">Live</span>
              </div>
              <div className="text-sm text-racing-silver">COTA</div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;