/**
 * Minimal MUI-like components when @mui/material is not available (e.g. install permission issues).
 * Replace imports from '@mui/material' with this file.
 */
import React from 'react';

const sx = (obj) => obj;
const styled = (Tag) => (style) => ({ children, ...rest }) => React.createElement(Tag, { style: { ...style, ...rest?.style }, ...rest }, children);

export const Box = ({ children, component = 'div', sx: sxProp, ...rest }) =>
  React.createElement(component, { style: sxProp || {}, ...rest }, children);
export const Paper = ({ children, sx: sxProp, ...rest }) =>
  React.createElement('div', { style: { padding: 16, background: '#fff', borderRadius: 4, boxShadow: '0 1px 3px rgba(0,0,0,0.12)', ...sxProp }, ...rest }, children);
export const Typography = ({ children, variant, component = 'p', ...rest }) =>
  React.createElement(component, { style: { margin: 0, fontSize: variant === 'h4' ? '2rem' : variant === 'h6' ? '1.25rem' : '1rem' }, ...rest }, children);
export const AppBar = ({ children, ...rest }) =>
  React.createElement('div', { style: { background: '#1976d2', color: '#fff', padding: '0 24px', position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1100 }, ...rest }, children);
export const Toolbar = ({ children, ...rest }) =>
  React.createElement('div', { style: { minHeight: 64, display: 'flex', alignItems: 'center' }, ...rest }, children);
export const Drawer = ({ children, variant, ...rest }) =>
  React.createElement('div', { style: { width: 240, flexShrink: 0, borderRight: '1px solid #e0e0e0' }, ...rest }, children);
export const List = ({ children, ...rest }) => React.createElement('ul', { style: { listStyle: 'none', padding: 0, margin: 0 }, ...rest }, children);
export const ListItem = ({ children, button, component = 'li', ...rest }) =>
  React.createElement(component, { style: { padding: '8px 16px', cursor: button ? 'pointer' : 'default', textDecoration: 'none', color: 'inherit' }, ...rest }, children);
export const ListItemIcon = ({ children, ...rest }) =>
  React.createElement('span', { style: { marginRight: 16, display: 'inline-flex' }, ...rest }, children);
export const ListItemText = ({ primary, ...rest }) =>
  React.createElement('span', { ...rest }, primary);
export const CssBaseline = () => null;
export const ThemeProvider = ({ children }) => React.createElement(React.Fragment, null, children);
export const createTheme = () => ({ palette: {} });
export const Card = ({ children, sx: sxProp, ...rest }) =>
  React.createElement('div', { style: { padding: 16, borderRadius: 4, boxShadow: '0 1px 3px rgba(0,0,0,0.12)', ...sxProp }, ...rest }, children);
export const CardContent = ({ children, ...rest }) => React.createElement('div', { ...rest }, children);
export const Grid = ({ children, container, item, xs, sm, md, spacing = 2, ...rest }) => {
  const base = (n) => ({ flex: `0 0 ${(n/12)*100}%`, maxWidth: `${(n/12)*100}%`, boxSizing: 'border-box' });
  const style = container ? { display: 'flex', flexWrap: 'wrap', gap: spacing * 8 } : item ? { ...(xs && base(xs)), ...(md && base(md)), padding: 4 } : {};
  return React.createElement('div', { style, ...rest }, children);
};
export const CircularProgress = () => React.createElement('div', { style: { width: 40, height: 40, border: '3px solid #eee', borderTopColor: '#1976d2', borderRadius: '50%', animation: 'spin 0.8s linear infinite' } });
export const Button = ({ children, variant, startIcon, color, ...rest }) =>
  React.createElement('button', { style: { padding: '8px 16px', background: color === 'primary' ? '#1976d2' : '#eee', color: color === 'primary' ? '#fff' : '#000', border: 'none', borderRadius: 4, cursor: 'pointer' }, ...rest }, startIcon, ' ', children);
export const TextField = ({ label, value, onChange, fullWidth, multiline, rows, ...rest }) =>
  React.createElement('div', { style: { marginBottom: 16 } },
    label && React.createElement('label', { style: { display: 'block', marginBottom: 4 } }, label),
    React.createElement(multiline ? 'textarea' : 'input', {
      value: value ?? '',
      onChange: e => onChange && onChange({ target: e.target }),
      style: { width: fullWidth ? '100%' : undefined, boxSizing: 'border-box' },
      rows: multiline ? (rows || 3) : undefined,
      ...rest
    })
  );
export const Dialog = ({ open, onClose, children, maxWidth, fullWidth }) => !open ? null : React.createElement('div', { style: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1300 }, onClick: onClose },
  React.createElement('div', { style: { background: '#fff', padding: 24, borderRadius: 8, minWidth: 400, maxWidth: fullWidth ? '90vw' : 400 }, onClick: e => e.stopPropagation() }, children));
export const DialogTitle = ({ children, ...rest }) => React.createElement('h2', { style: { margin: '0 0 16px' }, ...rest }, children);
export const DialogContent = ({ children, ...rest }) => React.createElement('div', { ...rest }, children);
export const DialogActions = ({ children, ...rest }) => React.createElement('div', { style: { marginTop: 16, display: 'flex', justifyContent: 'flex-end', gap: 8 }, ...rest }, children);
export const Select = ({ value, onChange, label, children, ...rest }) =>
  React.createElement('select', { value, onChange: e => onChange && onChange({ target: e.target }), ...rest }, children);
export const MenuItem = ({ children, value, ...rest }) => React.createElement('option', { value, ...rest }, children);
export const FormControl = ({ children, fullWidth, ...rest }) => React.createElement('div', { style: { width: fullWidth ? '100%' : undefined, marginBottom: 16 }, ...rest }, children);
export const InputLabel = ({ children, ...rest }) => React.createElement('label', { ...rest }, children);
export const Table = ({ children, ...rest }) => React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' }, ...rest }, children);
export const TableHead = ({ children, ...rest }) => React.createElement('thead', { ...rest }, children);
export const TableBody = ({ children, ...rest }) => React.createElement('tbody', { ...rest }, children);
export const TableRow = ({ children, ...rest }) => React.createElement('tr', { ...rest }, children);
export const TableCell = ({ children, ...rest }) => React.createElement('td', { style: { padding: 8, borderBottom: '1px solid #eee' }, ...rest }, children);
export const TableContainer = ({ children, component: C = 'div', ...rest }) => React.createElement(C, { ...rest }, children);
export const IconButton = ({ children, onClick, size, color, ...rest }) =>
  React.createElement('button', { onClick, style: { background: 'none', border: 'none', cursor: 'pointer', padding: size === 'small' ? 4 : 8 }, ...rest }, children);
export const Chip = ({ label, size, color, ...rest }) =>
  React.createElement('span', { style: { padding: '4px 8px', borderRadius: 16, fontSize: 12, background: color === 'success' ? '#4caf50' : color === 'error' ? '#f44336' : '#e0e0e0', color: '#fff' }, ...rest }, label);
export const Timeline = ({ children, ...rest }) => React.createElement('div', { ...rest }, children);
export const TimelineItem = ({ children, ...rest }) => React.createElement('div', { style: { marginBottom: 16 }, ...rest }, children);
export const TimelineSeparator = ({ children, ...rest }) => React.createElement('div', { ...rest }, children);
export const TimelineConnector = () => React.createElement('div', { style: { width: 2, background: '#e0e0e0', flexGrow: 1 } });
export const TimelineContent = ({ children, ...rest }) => React.createElement('div', { ...rest }, children);
export const TimelineDot = ({ children, color, ...rest }) =>
  React.createElement('div', { style: { width: 12, height: 12, borderRadius: '50%', background: color === 'success' ? '#4caf50' : color === 'error' ? '#f44336' : '#9e9e9e' }, ...rest }, children);
