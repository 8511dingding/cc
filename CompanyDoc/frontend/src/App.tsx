import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Documents from './pages/Documents';
import Templates from './pages/Templates';
import Terms from './pages/Terms';
import Customers from './pages/Customers';
import Uploads from './pages/Uploads';
import Statistics from './pages/Statistics';
import './App.css';

type MenuId = 'documents' | 'templates' | 'terms' | 'customers' | 'uploads' | 'statistics';

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
      case 'customers':
        return <Customers />;
      case 'uploads':
        return <Uploads />;
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