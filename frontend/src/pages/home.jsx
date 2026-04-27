import { useState } from "react"
import { useNavigate } from "react-router-dom";
import "./home.css"

export function Home() {
    const [destination1, setdestination1] = useState("");
    const [destination2, setdestination2] = useState("");
    const navigate = useNavigate();

    return (
        <div className="home-container">
            <div className="form-wrapper">
                <h1 className="title">Find Your Journey</h1>
                <div className="input-group">
                    <input
                        type="text"
                        className="input-field"
                        placeholder="Enter departure location"
                        value={destination1}
                        onChange={(e) => setdestination1(e.target.value)}
                    />
                    
                    <button className="swap-btn" onClick={() => {
                        setdestination1(destination2);
                        setdestination2(destination1);
                    }}>Swap</button>

                    <input
                        type="text"
                        className="input-field"
                        placeholder="Enter destination"
                        value={destination2}
                        onChange={(e) => setdestination2(e.target.value)}
                    />
                    <button className="submit-btn" onClick={() => navigate("/trains")}>Search Journey</button>
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