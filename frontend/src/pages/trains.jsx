import { useState ,useEffect, use} from "react"
import "./trains.css"

export function Trains() {
    const[trains, setTrains] = useState([]);   
    
    useEffect(() => {
        fetch("http://localhost:8080/api/trains")
            .then(response => response.json())
            .then(data => setTrains(data))
            .catch(error => console.error("Error fetching trains:", error));
    }, []);
    return (
        <div className="trains-container">
            <h1 className="trains-title">Available Trains</h1>
            <div className="trains-grid">
                {trains.map(train => (
                    <div key={train.id} className="train-card">
                        <div className="train-card-header">
                            <h2 className="train-name">{train.name}</h2>
                            <span className="train-badge">Active</span>
                        </div>
                        <div className="train-card-body">
                            <div className="train-detail">
                                <span className="detail-label">Departure:</span>
                                <span className="detail-value">{train.departure}</span>
                            </div>
                            <div className="train-detail">
                                <span className="detail-label">Arrival:</span>
                                <span className="detail-value">{train.arrival}</span>
                            </div>
                        </div>
                        <button className="book-btn">Book Now</button>
                    </div>
                ))}
            </div>
        </div>
    );
}