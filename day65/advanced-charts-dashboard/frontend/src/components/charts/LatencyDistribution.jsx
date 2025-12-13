import React from 'react';
import { Box } from '@mui/material';
import * as d3 from 'd3';

export default function LatencyDistribution({ data }) {
  const svgRef = React.useRef();

  React.useEffect(() => {
    if (!data || !svgRef.current) return;

    const margin = { top: 50, right: 30, bottom: 70, left: 60 };
    const width = 500 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
      .range([0, width])
      .domain(data.distributions.map(d => d.service))
      .padding(0.3);

    const y = d3.scaleLinear()
      .range([height, 0])
      .domain([0, d3.max(data.distributions, d => d.max)]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    svg.append('g')
      .call(d3.axisLeft(y));

    data.distributions.forEach(dist => {
      const center = x(dist.service) + x.bandwidth() / 2;
      const boxWidth = x.bandwidth() * 0.6;

      // Box
      svg.append('rect')
        .attr('x', center - boxWidth / 2)
        .attr('y', y(dist.q3))
        .attr('width', boxWidth)
        .attr('height', y(dist.q1) - y(dist.q3))
        .attr('fill', '#3b82f6')
        .attr('opacity', 0.7);

      // Median line
      svg.append('line')
        .attr('x1', center - boxWidth / 2)
        .attr('x2', center + boxWidth / 2)
        .attr('y1', y(dist.median))
        .attr('y2', y(dist.median))
        .attr('stroke', '#1e40af')
        .attr('stroke-width', 2);

      // Whiskers
      svg.append('line')
        .attr('x1', center)
        .attr('x2', center)
        .attr('y1', y(dist.q3))
        .attr('y2', y(dist.max))
        .attr('stroke', '#1e40af');

      svg.append('line')
        .attr('x1', center)
        .attr('x2', center)
        .attr('y1', y(dist.q1))
        .attr('y2', y(dist.min))
        .attr('stroke', '#1e40af');

      // Outliers
      dist.outliers.slice(0, 5).forEach(outlier => {
        svg.append('circle')
          .attr('cx', center + (Math.random() - 0.5) * boxWidth)
          .attr('cy', y(outlier))
          .attr('r', 3)
          .attr('fill', '#ef4444')
          .attr('opacity', 0.6);
      });
    });

  }, [data]);

  return (
    <Box sx={{ overflow: 'auto' }}>
      <svg ref={svgRef}></svg>
    </Box>
  );
}
