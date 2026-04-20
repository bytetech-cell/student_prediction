import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Predict from './pages/Predict';
import StudyPlan from './pages/StudyPlan';
import Analytics from './pages/Analytics';

function App() {
  const [role, setRole] = useState('student');

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout role={role} setRole={setRole} />}>
          <Route index element={<Home />} />
          <Route path="predict" element={<Predict />} />
          <Route path="study-plan" element={<StudyPlan />} />
          <Route path="analytics" element={<Analytics role={role} />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
