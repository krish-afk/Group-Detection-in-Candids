// import logo from './logo.svg';
// import './App.css';
// import Home from './components/Home';

// function App() {
//   return (
//     <div className="App">
//       <Home/>
//     </div>
//   );
// }

// export default App;

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Gallery from "./components/Gallery";
import logo from './logo.svg';
import './App.css';
import Home from './components/Home';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/gallery" element={<Gallery />} />
            </Routes>
        </Router>
    );
}

export default App;
