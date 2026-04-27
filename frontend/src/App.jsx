import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Home } from "./pages/home"
import { Trains } from "./pages/trains";
function App() {
 

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/trains" element={<Trains/>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
