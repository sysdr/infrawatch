import React from 'react';
import {
  Box,
  Typography,
  Chip
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import { formatDistanceToNow } from 'date-fns';

function EventTimeline({ events }) {
  const getEventColor = (severity) => {
    if (severity >= 60) return 'error';
    if (severity >= 40) return 'warning';
    return 'success';
  };

  if (!events || events.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 5, color: 'text.secondary' }}>
        <Typography>No recent events</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxHeight: 500, overflow: 'auto' }}>
      <Timeline>
        {events.slice(0, 20).map((event, index) => (
          <TimelineItem key={event.event_id}>
            <TimelineOppositeContent color="text.secondary" sx={{ flex: 0.3 }}>
              <Typography variant="caption">
                {formatDistanceToNow(new Date(event.timestamp))} ago
              </Typography>
            </TimelineOppositeContent>
            
            <TimelineSeparator>
              <TimelineDot color={getEventColor(event.severity)} />
              {index < events.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            
            <TimelineContent>
              <Typography variant="subtitle2" fontWeight="bold">
                {event.event_type} - {event.action}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {event.user_id || 'Anonymous'} | {event.ip_address}
              </Typography>
              <Box sx={{ mt: 0.5 }}>
                <Chip
                  label={event.success ? 'Success' : 'Failed'}
                  size="small"
                  color={event.success ? 'success' : 'error'}
                />
                {event.severity > 0 && (
                  <Chip
                    label={`Severity: ${event.severity}`}
                    size="small"
                    color={getEventColor(event.severity)}
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Box>
  );
}

export default EventTimeline;
