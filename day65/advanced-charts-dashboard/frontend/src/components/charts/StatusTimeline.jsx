import React from 'react';
import { Box } from '@mui/material';
import * as d3 from 'd3';

export default function StatusTimeline({ data }) {
  const svgRef = React.useRef();

  React.useEffect(() => {
    if (!data || !svgRef.current) return;

    const margin = { top: 50, right: 30, bottom: 70, left: 120 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const services = data.timeline.map(t => t.service);
    const allEvents = data.timeline.flatMap(t => t.events);
    const timeExtent = d3.extent(allEvents.flatMap(e => [
      new Date(e.start),
      new Date(e.end)
    ]));

    const x = d3.scaleTime()
      .range([0, width])
      .domain(timeExtent);

    const y = d3.scaleBand()
      .range([0, height])
      .domain(services)
      .padding(0.2);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat('%H:%M')));

    svg.append('g')
      .call(d3.axisLeft(y));

    data.timeline.forEach(timeline => {
      timeline.events.forEach(event => {
        const startTime = new Date(event.start);
        const endTime = new Date(event.end);

        svg.append('rect')
          .attr('x', x(startTime))
          .attr('y', y(timeline.service))
          .attr('width', x(endTime) - x(startTime))
          .attr('height', y.bandwidth())
          .attr('fill', event.color)
          .attr('opacity', 0.8)
          .attr('rx', 4);
      });
    });

  }, [data]);

  return (
    <Box sx={{ overflow: 'auto' }}>
      <svg ref={svgRef}></svg>
    </Box>
  );
}
