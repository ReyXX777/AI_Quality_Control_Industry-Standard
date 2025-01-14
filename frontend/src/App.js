import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import QualityStandards from './components/QualityStandards';
import MaintenancePrediction from './components/MaintenancePrediction';
import DefectDetection from './components/DefectDetection';
import Settings from './components/Settings';
import Footer from './components/Footer';
import './App.css';

const App = () => {
    const [language, setLanguage] = useState('en');

    const handleLanguageChange = (e) => {
        setLanguage(e.target.value);
    };

    return (
        <Router>
            <div className="app">
                <Navbar />
                <div className="content">
                    <div className="language-selector">
                        <label htmlFor="language">Select Language: </label>
                        <select id="language" value={language} onChange={handleLanguageChange}>
                            <option value="en">English</option>
                            <option value="hi">हिंदी</option>
                        </select>
                    </div>

                    <Switch>
                        <Route exact path="/" component={Home} />
                        <Route path="/quality-standards" component={QualityStandards} />
                        <Route path="/maintenance" component={MaintenancePrediction} />
                        <Route path="/defect-detection" component={DefectDetection} />
                        <Route path="/settings" component={Settings} />
                    </Switch>
                </div>
                <Footer />
            </div>
        </Router>
    );
};

export default App;
