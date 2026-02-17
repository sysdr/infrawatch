import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Box } from '@mui/material';

const DependencyGraph = ({ correlations }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!correlations || correlations.length === 0) return;

    const width = 600;
    const height = 450;

    // Clear previous content
    d3.select(svgRef.current).selectAll("*").remove();

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Extract nodes and links
    const nodesMap = new Map();
    const links = [];

    correlations.slice(0, 15).forEach(corr => {
      if (!nodesMap.has(corr.metric_a.id)) {
        nodesMap.set(corr.metric_a.id, {
          id: corr.metric_a.id,
          name: corr.metric_a.name,
          group: 1
        });
      }
      if (!nodesMap.has(corr.metric_b.id)) {
        nodesMap.set(corr.metric_b.id, {
          id: corr.metric_b.id,
          name: corr.metric_b.name,
          group: 2
        });
      }

      links.push({
        source: corr.metric_a.id,
        target: corr.metric_b.id,
        value: Math.abs(corr.coefficient)
      });
    });

    const nodes = Array.from(nodesMap.values());

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.value) * 3);

    // Create nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node.append('circle')
      .attr('r', 20)
      .attr('fill', d => d.group === 1 ? '#667eea' : '#f093fb')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    node.append('text')
      .text(d => d.name.split('.')[0])
      .attr('x', 0)
      .attr('y', 30)
      .attr('text-anchor', 'middle')
      .attr('font-size', '10px')
      .attr('fill', '#333');

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

  }, [correlations]);

  if (!correlations || correlations.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={400}>
        <div style={{ textAlign: 'center', color: '#999' }}>
          <p>No dependency network available</p>
          <p style={{ fontSize: '0.9em' }}>Correlations will appear here once detected</p>
        </div>
      </Box>
    );
  }

  return (
    <Box display="flex" justifyContent="center">
      <svg ref={svgRef}></svg>
    </Box>
  );
};

export default DependencyGraph;
