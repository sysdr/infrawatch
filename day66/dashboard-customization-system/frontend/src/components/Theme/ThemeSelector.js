import React from 'react';
import { Box, Button, Menu, MenuItem, Typography } from '@mui/material';
import PaletteIcon from '@mui/icons-material/Palette';
import { useTheme } from '../../contexts/ThemeContext';

const ThemeSelector = ({ onThemeChange }) => {
  const { currentTheme, setCurrentTheme, themes } = useTheme();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleThemeSelect = (themeName) => {
    setCurrentTheme(themeName);
    if (onThemeChange) {
      onThemeChange(themeName);
    }
    handleClose();
  };

  return (
    <Box>
      <Button
        startIcon={<PaletteIcon />}
        onClick={handleClick}
        sx={{ color: 'var(--text)' }}
      >
        Theme: {currentTheme}
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        {Object.keys(themes).map((themeName) => (
          <MenuItem
            key={themeName}
            onClick={() => handleThemeSelect(themeName)}
            selected={themeName === currentTheme}
          >
            <Typography textTransform="capitalize">{themeName}</Typography>
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
};

export default ThemeSelector;
