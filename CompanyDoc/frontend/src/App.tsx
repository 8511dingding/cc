import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Documents from './pages/Documents';
import Templates from './pages/Templates';
import Terms from './pages/Terms';
import Approvals from './pages/Approvals';
import Statistics from './pages/Statistics';
import './App.css';

type MenuId = 'documents' | 'templates' | 'terms' | 'approvals' | 'statistics';

function App() {
  const [activeMenu, setActiveMenu] = useState<MenuId>('documents');

  const renderPage = () => {
    switch (activeMenu) {
      case 'documents':
        return <Documents />;
      case 'templates':
        return <Templates />;
      case 'terms':
        return <Terms />;
      case 'approvals':
        return <Approvals />;
      case 'statistics':
        return <Statistics />;
      default:
        return <Documents />;
    }
  };

  return (
    <div className="app">
      <Sidebar activeMenu={activeMenu} onMenuChange={(id) => setActiveMenu(id as MenuId)} />
      <main className="main-content">{renderPage()}</main>
    </div>
  );
}

export default App;