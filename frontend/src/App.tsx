import { useEffect, useState } from "react";
import "./App.css";

type SensorData = {
  id: number;
  light_level: number;
  created_at: string;
};

function App() {
  const [data, setData] = useState<SensorData | null>(null);

  useEffect(() => {
    const fetchSensorData = () => {
      fetch("http://127.0.0.1:8000/api/sensor/latest")
        .then((response) => response.json())
        .then((json) => setData(json));
    };

    // 最初に1回取得
    fetchSensorData();

    // 5秒ごとに取得
    const intervalId = setInterval(fetchSensorData, 5000);

    // コンポーネントが消えたらタイマーを解除
    return () => {
      clearInterval(intervalId);
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
        {data ? "光" : "Now Loading"}
      </div>
    </div>
  );
}

export default App;