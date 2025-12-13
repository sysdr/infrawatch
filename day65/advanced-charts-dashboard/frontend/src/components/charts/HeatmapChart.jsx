import React from 'react';
import { Box } from '@mui/material';
import * as d3 from 'd3';

export default function HeatmapChart({ data }) {
  const svgRef = React.useRef();

  React.useEffect(() => {
    if (!data || !svgRef.current) return;

    const margin = { top: 50, right: 30, bottom: 70, left: 60 };
    const width = 900 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const days = [...new Set(data.data.map(d => d.day))];
    const hours = [...new Set(data.data.map(d => d.hour))];

    const x = d3.scaleBand()
      .range([0, width])
      .domain(hours)
      .padding(0.05);

    const y = d3.scaleBand()
      .range([0, height])
      .domain(days)
      .padding(0.05);

    const colorScale = d3.scaleSequential()
      .interpolator(d3.interpolateBlues)
      .domain([data.value_range.min, data.value_range.max]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).tickSize(0))
      .select('.domain').remove();

    svg.append('g')
      .call(d3.axisLeft(y).tickSize(0))
      .select('.domain').remove();

    svg.selectAll('rect')
      .data(data.data)
      .enter()
      .append('rect')
      .attr('x', d => x(d.hour))
      .attr('y', d => y(d.day))
      .attr('width', x.bandwidth())
      .attr('height', y.bandwidth())
      .style('fill', d => colorScale(d.value))
      .style('stroke', '#fff')
      .style('stroke-width', 1)
      .on('mouseover', function(event, d) {
        d3.select(this).style('opacity', 0.8);
      })
      .on('mouseout', function() {
        d3.select(this).style('opacity', 1);
      });

    svg.append('text')
      .attr('x', width / 2)
      .attr('y', -30)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text(`${data.metric} - Hour of Day vs Day of Week`);

  }, [data]);

  return (
    <Box sx={{ overflow: 'auto' }}>
      <svg ref={svgRef}></svg>
    </Box>
  );
}
