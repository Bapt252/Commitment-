import React from 'react';
import Navigation from './Navigation';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <div className="flex-grow">
        {children}
      </div>
    </div>
  );
};

export default Layout;
