import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';
import * as d3 from 'd3';
import { fetchTopology, fetchDependencies } from '../services/api';

function TopologyGraph() {
  const svgRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);
  const [dependencies, setDependencies] = useState([]);

  useEffect(() => {
    loadTopology();
  }, []);

  const loadTopology = async () => {
    const data = await fetchTopology();
    renderGraph(data);
  };

  const handleNodeClick = async (node) => {
    setSelectedNode(node);
    const deps = await fetchDependencies(node.id);
    setDependencies(deps.dependencies || []);
  };

  const renderGraph = (data) => {
    const width = 800;
    const height = 600;

    // Clear previous
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Color scale
    const colorScale = d3.scaleOrdinal()
      .domain(['instance', 'load_balancer', 'database', 'security_group'])
      .range(['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']);

    // Force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Links
    const link = svg.append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', 15)
      .attr('fill', d => colorScale(d.type))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (event, d) => handleNodeClick(d))
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Labels
    const label = svg.append('g')
      .selectAll('text')
      .data(data.nodes)
      .join('text')
      .text(d => d.name)
      .attr('font-size', 10)
      .attr('dx', 20)
      .attr('dy', 4);

    // Update positions
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" mb={3}>
        Infrastructure Topology Map
      </Typography>

      <Box display="flex" gap={2}>
        <Paper sx={{ flex: 1, p: 2, height: 600 }}>
          <svg ref={svgRef} style={{ border: '1px solid #ddd' }}></svg>
        </Paper>

        {selectedNode && (
          <Paper sx={{ width: 300, p: 2, height: 600, overflow: 'auto' }}>
            <Typography variant="h6" mb={2}>
              {selectedNode.name}
            </Typography>
            <Chip label={selectedNode.type} color="primary" size="small" sx={{ mb: 2 }} />
            
            <Typography variant="subtitle2" mt={2} mb={1}>
              Dependencies ({dependencies.length})
            </Typography>
            {dependencies.map((dep, idx) => (
              <Box key={idx} mb={1}>
                <Typography variant="body2">
                  → {dep.name} ({dep.type})
                </Typography>
              </Box>
            ))}
          </Paper>
        )}
      </Box>
    </Box>
  );
}

export default TopologyGraph;
