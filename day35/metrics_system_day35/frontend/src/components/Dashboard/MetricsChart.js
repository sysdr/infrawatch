import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Container = styled.div`
  padding: 20px;
`;

const ChartTitle = styled.h3`
  color: #1d2327;
  font-size: 18px;
  margin-bottom: 15px;
  border-bottom: 1px solid #c3c4c7;
  padding-bottom: 10px;
`;

function MetricsChart() {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: []
  });

  useEffect(() => {
    // Generate sample data
    const now = new Date();
    const labels = [];
    const successData = [];
    const failureData = [];

    for (let i = 11; i >= 0; i--) {
      const time = new Date(now - i * 5 * 60 * 1000);
      labels.push(time.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }));
      successData.push(Math.floor(Math.random() * 50) + 80);
      failureData.push(Math.floor(Math.random() * 10) + 2);
    }

    setChartData({
      labels,
      datasets: [
        {
          label: 'Successful Tasks',
          data: successData,
          borderColor: '#00a32a',
          backgroundColor: 'rgba(0, 163, 42, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Failed Tasks',
          data: failureData,
          borderColor: '#d63638',
          backgroundColor: 'rgba(214, 54, 56, 0.1)',
          tension: 0.4,
        }
      ]
    });
  }, []);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <Container>
      <ChartTitle>Task Processing Metrics</ChartTitle>
      <Line data={chartData} options={options} />
    </Container>
  );
}

export default MetricsChart;
