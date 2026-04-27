import { useState } from "react"
import "./home.css"

export function Home() {
   const [destination1, setdestination1] = useState("");
   const [destination2, setdestination2] = useState("");
   
   return (
    <div className="home-container">
        <div className="form-wrapper">
            <h1 className="title">Journey Planner</h1>
            <div className="input-group">
                <input 
                  type="text" 
                  className="input-field"
                  placeholder="Enter departure location" 
                  value={destination1}
                  onChange={(e) => setdestination1(e.target.value)} 
                />
                <input 
                  type="text" 
                  className="input-field"
                  placeholder="Enter destination" 
                  value={destination2}
                  onChange={(e) => setdestination2(e.target.value)} 
                />
                <button className="submit-btn">Search Journey</button>
            </div>
            {destination1 && destination2 && (
              <div className="route-info">
                <p>From: <strong>{destination1}</strong></p>
                <p>To: <strong>{destination2}</strong></p>
              </div>
            )}
        </div>
    </div>
   );
}