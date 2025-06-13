import { rest } from 'msw';

export const handlers = [
  // Health check endpoint
  rest.get('/health', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({ status: 'healthy', service: 'log-processor' })
    );
  }),

  // Get log events
  rest.get('/logs', (req, res, ctx) => {
    const mockLogs = [
      {
        id: 1,
        message: 'Application started',
        level: 'INFO',
        timestamp: new Date().toISOString(),
        source: 'app',
        metadata: null,
      },
      {
        id: 2,
        message: 'Database connection established',
        level: 'INFO',
        timestamp: new Date().toISOString(),
        source: 'database',
        metadata: null,
      },
    ];

    return res(ctx.status(200), ctx.json(mockLogs));
  }),

  // Create log event
  rest.post('/logs', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        message: req.body.message,
        level: req.body.level || 'INFO',
        timestamp: new Date().toISOString(),
        source: req.body.source,
        metadata: req.body.metadata,
      })
    );
  }),
];
