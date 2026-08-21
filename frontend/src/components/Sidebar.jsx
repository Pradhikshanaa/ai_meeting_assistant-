import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Video, CheckSquare, Sparkles, CheckCircle2, Bell } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { isLeader } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand-icon">
          <Sparkles size={20} color="white" />
        </div>
        <div>
          <div className="sidebar-title">Smart AI Assistant</div>
          <div className="sidebar-subtitle">Meeting Intelligence</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/team"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Users size={18} />
          <span>My Team</span>
        </NavLink>

        <NavLink
          to="/meetings"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Video size={18} />
          <span>Meetings</span>
        </NavLink>

        <NavLink
          to="/tasks"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <CheckSquare size={18} />
          <span>{isLeader ? 'Team Tasks' : 'My Tasks'}</span>
        </NavLink>

        {isLeader && (
          <NavLink
            to="/approvals"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <CheckCircle2 size={18} />
            <span>Approvals</span>
          </NavLink>
        )}

        <NavLink
          to="/pex"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          style={{ backgroundColor: 'rgba(99, 102, 241, 0.1)', color: '#818cf8', fontWeight: 600 }}
        >
          <Sparkles size={18} color="#818cf8" />
          <span>Pex AI</span>
        </NavLink>

        <NavLink
          to="/notifications"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Bell size={18} />
          <span>Notifications</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div>College Mini Project</div>
        <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '2px' }}>
          Role: {isLeader ? 'Leader (Full Access)' : 'Employee (Restricted)'}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
