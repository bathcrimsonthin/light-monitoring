import { useEffect, useState } from "react";
import "./App.css";

type SensorData = {
  id: number;
  light_level: number;
  created_at: string;
};

function App() {
  const [data, setData] = useState<SensorData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/sensor");

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      const json = JSON.parse(event.data);

      console.log("Received:", json);

      setData(json);
      setLoading(false);
    };

    ws.onerror = () => {
      console.log("WebSocket error");
      setLoading(true);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setLoading(true);
    };

    return () => {
      ws.close();
    };
  }, []);

  const light_level = data ? data.light_level / 4095.0 : 0.0;

  const lightStyle = {
    opacity: 0.2 + 100 * light_level / 125,
  };

  return (
    <div className="app">
      <div className="light" style={lightStyle}></div>

      <div className="light-text">
        {loading ? "Now Loading" : "光"}
      </div>
    </div>
  );
}

export default App;