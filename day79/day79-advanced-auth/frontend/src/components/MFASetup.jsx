import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Alert
} from '@mui/material';
import { QRCodeSVG } from 'qrcode.react';
import axios from 'axios';

const MFASetup = ({ userId }) => {
  const [secret, setSecret] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [step, setStep] = useState(1);
  const [error, setError] = useState('');
  const [currentTOTP, setCurrentTOTP] = useState('');

  // Function to generate current TOTP code (for testing without app)
  const generateCurrentTOTP = async () => {
    if (!secret) return;
    try {
      setError(''); // Clear any previous errors
      // Call backend to generate current TOTP from secret
      const response = await axios.post(`http://localhost:8000/api/auth/mfa/generate-code?secret=${encodeURIComponent(secret)}`);
      if (response.data.code) {
        const generatedCode = response.data.code;
        setVerificationCode(generatedCode);
        setCurrentTOTP(generatedCode);
        
        // Auto-verify immediately after generating to avoid expiration
        // Use a small delay to ensure state is updated
        setTimeout(async () => {
          try {
            const url = `http://localhost:8000/api/auth/mfa/verify?user_id=${encodeURIComponent(userId)}&token=${encodeURIComponent(generatedCode)}`;
            await axios.post(url);
            setStep(3);
            setError('');
          } catch (verifyErr) {
            console.error('Auto-verify error:', verifyErr);
            // Don't set error here - let user manually verify if auto-verify fails
            setError('Code generated. Please click "Verify and Enable MFA" button.');
          }
        }, 300);
      }
    } catch (err) {
      console.error('Failed to generate TOTP:', err);
      setError('Failed to generate code: ' + (err.response?.data?.detail || err.message));
    }
  };

  useEffect(() => {
    if (userId) {
      setupMFA();
    } else {
      setError('User ID is required');
    }
  }, [userId]);

  const setupMFA = async () => {
    if (!userId) {
      setError('User ID is required');
      console.error('MFASetup: userId is missing', { userId });
      return;
    }
    try {
      // Use URL with query parameters directly
      const url = `http://localhost:8000/api/auth/mfa/setup?user_id=${encodeURIComponent(userId)}`;
      const response = await axios.post(url);
      setSecret(response.data.secret);
      setQrCode(response.data.qr_code);
      setBackupCodes(response.data.backup_codes);
      setError('');
    } catch (err) {
      console.error('MFA setup error:', err);
      setError('Failed to setup MFA: ' + (err.response?.data?.detail || err.message));
    }
  };

  const verifyMFA = async () => {
    if (!userId) {
      setError('User ID is required');
      return;
    }
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a 6-digit verification code');
      return;
    }
    try {
      // Use URL with query parameters directly
      const url = `http://localhost:8000/api/auth/mfa/verify?user_id=${encodeURIComponent(userId)}&token=${encodeURIComponent(verificationCode)}`;
      await axios.post(url);
      setStep(3);
      setError('');
    } catch (err) {
      console.error('MFA verify error:', err);
      const errorMsg = err.response?.data?.detail || err.message;
      if (errorMsg.includes('expired')) {
        setError('Code expired. Please click "Generate & Auto-Fill Verification Code" again to get a fresh code.');
      } else {
        setError('Invalid verification code: ' + errorMsg);
      }
    }
  };

  return (
    <Box sx={{ maxWidth: 600, margin: '0 auto', mt: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Setup Multi-Factor Authentication
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {step === 1 && (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2" component="div">
                  <strong>No TOTP app? No problem!</strong> You can proceed without scanning the QR code. 
                  We'll generate a verification code for you automatically.
                </Typography>
              </Alert>

              {secret && (
                <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2, border: '1px solid', borderColor: 'grey.300' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Your Secret Key (for manual entry if needed):
                  </Typography>
                  <Box sx={{ 
                    p: 1.5, 
                    bgcolor: 'white', 
                    borderRadius: 1, 
                    border: '1px solid', 
                    borderColor: 'grey.400',
                    fontFamily: 'monospace',
                    fontSize: '1.1em',
                    textAlign: 'center',
                    wordBreak: 'break-all'
                  }}>
                    {secret}
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Save this key if you want to set up a TOTP app later (Google Authenticator, Authy, etc.)
                  </Typography>
                </Box>
              )}

              {qrCode && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    <strong>Optional:</strong> If you have a TOTP app, scan this QR code:
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                    <img src={`data:image/png;base64,${qrCode}`} alt="QR Code" style={{ maxWidth: '200px' }} />
                  </Box>
                </Box>
              )}

              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={() => setStep(2)}
                sx={{ mt: 2 }}
              >
                Continue to Verification (No App Required)
              </Button>
            </Box>
          )}

          {step === 2 && (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                <Typography variant="body2" component="div">
                  <strong>Easy Setup - No App Required!</strong>
                  <br />
                  Click the button below to automatically generate and fill in the verification code.
                </Typography>
              </Alert>

              {secret && (
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={generateCurrentTOTP}
                  sx={{ mb: 3 }}
                  color="primary"
                >
                  🔐 Generate & Auto-Fill Verification Code
                </Button>
              )}

              {currentTOTP && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  <Typography variant="body1">
                    ✅ Code Generated: <strong style={{fontSize: '1.2em'}}>{currentTOTP}</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    The code has been auto-filled below. Click "Verify and Enable MFA" to complete setup.
                  </Typography>
                </Alert>
              )}

              {!currentTOTP && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Click the button above to generate your verification code automatically, 
                    or enter a 6-digit code manually if you have a TOTP app set up.
                  </Typography>
                </Alert>
              )}

              <TextField
                fullWidth
                label="Verification Code (6 digits)"
                value={verificationCode}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setVerificationCode(value);
                }}
                placeholder="Click button above to auto-fill"
                inputProps={{ maxLength: 6, style: { textAlign: 'center', fontSize: '1.2em', letterSpacing: '0.2em' } }}
                sx={{ mb: 2 }}
                helperText={currentTOTP ? "Code has been auto-filled. Click verify below." : "Enter 6-digit code or click button above to generate"}
              />

              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Button
                  variant="outlined"
                  onClick={() => setStep(1)}
                >
                  ← Back
                </Button>
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={verifyMFA}
                  disabled={verificationCode.length !== 6}
                >
                  ✅ Verify and Enable MFA
                </Button>
              </Box>
            </Box>
          )}

          {step === 3 && (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>
                MFA successfully enabled!
              </Alert>
              <Typography variant="body1" paragraph>
                Save these backup codes in a secure location:
              </Typography>
              <Grid container spacing={2}>
                {backupCodes.map((code, index) => (
                  <Grid item xs={6} key={index}>
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: 'monospace',
                        p: 1,
                        bgcolor: 'grey.100',
                        borderRadius: 1
                      }}
                    >
                      {code}
                    </Typography>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default MFASetup;
