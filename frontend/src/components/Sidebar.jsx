import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import KPICommandCenter from './KPICommandCenter'
import KPIAllocationMatrix from './KPIAllocationMatrix'
import KPICashflowAnalytics from './KPICashflowAnalytics'

function Sidebar() {
  const location = useLocation()
  
  return (
    <div className="sidebar">
      <h1>💰 Finance App</h1>
      
      <nav>
        <Link to="/">Portfolio Command Center</Link>
        <Link to="/allocation_matrix">Allocation Matrix</Link>
        <Link to="/cashflow_analytics">Cashflow Analytics</Link>
      </nav>

      {location.pathname === '/allocation_matrix' ? (
        <KPIAllocationMatrix />
      ) : location.pathname === '/cashflow_analytics' ? (
        <KPICashflowAnalytics />
      ) : (
        <KPICommandCenter />
      )}
    </div>
  )
}

export default Sidebar
