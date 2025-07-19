// Browser Error Monitor for Auth Integration Dashboard
// Add this script to your HTML or include it in your React app

(function() {
    'use strict';
    
    console.log('🔍 Browser Error Monitor Started');
    
    // Store errors for reporting
    let errorLog = [];
    const MAX_ERRORS = 50;
    
    // Monitor console errors
    const originalError = console.error;
    const originalWarn = console.warn;
    
    console.error = function(...args) {
        const error = {
            type: 'error',
            message: args.join(' '),
            timestamp: new Date().toISOString(),
            stack: new Error().stack
        };
        
        errorLog.push(error);
        if (errorLog.length > MAX_ERRORS) {
            errorLog.shift();
        }
        
        // Send to monitoring endpoint if available
        sendErrorToServer(error);
        
        // Call original console.error
        originalError.apply(console, args);
    };
    
    console.warn = function(...args) {
        const warning = {
            type: 'warning',
            message: args.join(' '),
            timestamp: new Date().toISOString(),
            stack: new Error().stack
        };
        
        errorLog.push(warning);
        if (errorLog.length > MAX_ERRORS) {
            errorLog.shift();
        }
        
        // Call original console.warn
        originalWarn.apply(console, args);
    };
    
    // Monitor unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        const error = {
            type: 'unhandledrejection',
            message: event.reason?.message || event.reason || 'Unknown promise rejection',
            timestamp: new Date().toISOString(),
            stack: event.reason?.stack
        };
        
        errorLog.push(error);
        if (errorLog.length > MAX_ERRORS) {
            errorLog.shift();
        }
        
        sendErrorToServer(error);
    });
    
    // Monitor JavaScript errors
    window.addEventListener('error', function(event) {
        const error = {
            type: 'javascript_error',
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            timestamp: new Date().toISOString(),
            stack: event.error?.stack
        };
        
        errorLog.push(error);
        if (errorLog.length > MAX_ERRORS) {
            errorLog.shift();
        }
        
        sendErrorToServer(error);
    });
    
    // Monitor network errors
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args)
            .then(response => {
                if (!response.ok) {
                    const error = {
                        type: 'network_error',
                        message: `HTTP ${response.status}: ${response.statusText}`,
                        url: args[0],
                        timestamp: new Date().toISOString()
                    };
                    
                    errorLog.push(error);
                    if (errorLog.length > MAX_ERRORS) {
                        errorLog.shift();
                    }
                    
                    sendErrorToServer(error);
                }
                return response;
            })
            .catch(error => {
                const networkError = {
                    type: 'network_error',
                    message: error.message,
                    url: args[0],
                    timestamp: new Date().toISOString()
                };
                
                errorLog.push(networkError);
                if (errorLog.length > MAX_ERRORS) {
                    errorLog.shift();
                }
                
                sendErrorToServer(networkError);
                throw error;
            });
    };
    
    // Function to send errors to server
    function sendErrorToServer(error) {
        // Try to send to a monitoring endpoint if it exists
        fetch('/api/monitor/errors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                error: error,
                userAgent: navigator.userAgent,
                url: window.location.href,
                timestamp: new Date().toISOString()
            })
        }).catch(() => {
            // Silently fail if monitoring endpoint doesn't exist
        });
    }
    
    // Expose error log for debugging
    window.errorMonitor = {
        getErrors: () => errorLog,
        clearErrors: () => { errorLog = []; },
        getErrorCount: () => errorLog.length
    };
    
    // Log initial status
    console.log('✅ Browser Error Monitor Active - Monitoring console errors, network errors, and unhandled rejections');
    
})(); 